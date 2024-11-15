import json
import os

import pathway as pw


def remove_emails_from_data(payload):
    if isinstance(payload, str):
        # The string case is obvious: it's getting split and then merged back after
        # the email-like substrings are removed
        return " ".join([item for item in payload.split(" ") if "@" not in item])

    if isinstance(payload, list):
        # If the payload is a list, one needs to remove emails from each of its
        # elements and then return the result of the processing
        result = []
        for item in payload:
            result.append(remove_emails_from_data(item))
        return result

    if isinstance(payload, dict):
        # If the payload is a dict, one needs to remove emails from its keys and
        # values and then return the clean dict
        result = {}
        for key, value in payload.items():
            # There are no e-mails in the keys of the returned dict
            # So, we only need to remove them from values
            value = remove_emails_from_data(value)
            result[key] = value
        return result

    # If the payload is neither str nor list or dict, it's a primitive type:
    # namely, a boolean, a float, or an int. It can also be just null.
    #
    # But in any case, there is no data to remove from such an element.
    return payload


def remove_emails(raw_commit_data: pw.Json) -> pw.Json:
    # First, parse pw.Json type into a Python dict
    data = json.loads(raw_commit_data.as_str())

    # Next, just apply the recursive method to delete e-mails
    return remove_emails_from_data(data)


def extract_author_login(commit_data: pw.Json) -> str:
    if not commit_data["author"]:
        return ""
    return commit_data["author"]["login"].as_str()


def extract_commit_timestamp(commit_data: pw.Json) -> pw.DateTimeUtc:
    return pw.DateTimeUtc(commit_data["created_at"].as_str())


def replace_config_secrets():
    with open("./github-config.yaml", "r") as f:
        github_config = f.read()
    github_config = github_config.replace(
        "$GITHUB_PERSONAL_ACCESS_TOKEN",
        os.environ["GITHUB_PERSONAL_ACCESS_TOKEN"]
    )
    with open("./prepared-github-config.yaml", "w") as f:
        f.write(github_config)


if __name__ == "__main__":
    replace_config_secrets()    

    commits_table = pw.io.airbyte.read(
        "./prepared-github-config.yaml",
        streams=["commits"],
        enforce_method="pypi",
        mode=os.environ.get("INPUT_CONNECTOR_MODE", "static"),
    )
    commits_table = commits_table.select(data=pw.apply(remove_emails, pw.this.data))
    commits_table = commits_table.select(
        author_login=pw.apply(extract_author_login, pw.this.data),
        commit_timestamp=pw.apply(extract_commit_timestamp, pw.this.data),
        data=pw.this.data,
    )

    local_output_path = os.environ.get("LOCAL_OUTPUT_PATH")
    if local_output_path is not None:
        pw.io.deltalake.write(commits_table, local_output_path)

    # Delta table output to S3: works if the path is passed as an env var
    s3_output_path = os.environ.get("AWS_S3_OUTPUT_PATH")
    if s3_output_path is not None:
        credentials = pw.io.s3.AwsS3Settings(
            access_key=os.environ["AWS_S3_ACCESS_KEY"],
            secret_access_key=os.environ["AWS_S3_SECRET_ACCESS_KEY"],
            bucket_name=os.environ["AWS_BUCKET_NAME"],
            region=os.environ["AWS_REGION"],
        )
        pw.io.deltalake.write(
            commits_table, s3_output_path, s3_connection_settings=credentials
        )
    pw.run(monitoring_level=pw.MonitoringLevel.NONE)
