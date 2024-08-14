# Data Preparation for Spark Analytics

This repository contains modified example code for the ["Data Preparation for Spark Analytics"](https://pathway.com/developers/templates/delta_lake_etl) tutorial.

The changes were made to ensure the code can run in the cloud using the [Pathway BYOL](https://aws.amazon.com/marketplace/pp/prodview-qijbgoyohele4) container. This version of the code is designed to **extract** data from GitHub, **transform** it by removing sensitive information, and **load** the cleaned data into a Delta Lake hosted on S3.

## Running the Example

### Locally

To run this example locally, follow these steps:

1. Obtain your GitHub Personal Access Token (PAT) from the [Personal access tokens](https://github.com/settings/tokens) page.
2. Insert the token into the `personal_access_token` field in the `./github-config.yaml` file. A comment in the file provides guidance. Alternatively, you can store the token in the `GITHUB_PERSONAL_ACCESS_TOKEN` environment variable.
3. Get your Pathway License Key [here](https://pathway.com/features) (free tier of "Scale" plan) and store it in the `PATHWAY_LICENSE_KEY` environment variable.
4. Run the Python code in the `main.py` file. Ensure that the required environment variables are set. If you prefer to set them only for a single run, you can use the following command: `PATHWAY_LICENSE_KEY=YOUR_LICENSE_KEY GITHUB_PERSONAL_ACCESS_TOKEN=YOUR_GITHUB_PERSONAL_ACCESS_TOKEN python main.py`.

### Locally Without Code Checkout

If you have `pathway` installed, there's an easier way to run the code. You can use the `--repository-url` parameter in the command-line tool to launch it directly from the repository. However, you still need to provide your GitHub credentials and Pathway's license key. The launch command will look like this:

```bash
PATHWAY_LICENSE_KEY=YOUR_LICENSE_KEY \
GITHUB_PERSONAL_ACCESS_TOKEN=YOUR_GITHUB_PERSONAL_ACCESS_TOKEN \
pathway spawn --repository-url https://github.com/pathway-labs/airbyte-to-deltalake python main.py
```

## Adding S3

Since this example is intended to run in the cloud, local output isn't very useful. The data will remain on the cloud machine and be deleted once the container terminates. To retain the output, it's better to save it to S3 bucket. You can enable S3 output by specifying the following environment variables:

* `AWS_S3_OUTPUT_PATH`: The full output path in S3
* `AWS_S3_ACCESS_KEY`: Your S3 access key
* `AWS_S3_SECRET_ACCESS_KEY`: Your S3 secret access key
* `AWS_BUCKET_NAME`: The name of your S3 bucket
* `AWS_REGION`: The region of your S3 bucket

To run Docker locally, use the following command:

```bash
docker run \
    -e PATHWAY_LICENSE_KEY=YOUR_LICENSE_KEY \
    -e AWS_S3_OUTPUT_PATH=YOUR_OUTPUT_PATH_IN_S3_BUCKET \
    -e AWS_S3_ACCESS_KEY=YOUR_S3_ACCESS_KEY \
    -e AWS_S3_SECRET_ACCESS_KEY=YOUR_S3_SECRET_ACCESS_KEY \
    -e AWS_BUCKET_NAME=YOUR_BUCKET_NAME \
    -e AWS_REGION=YOUR_AWS_REGION \
    -t pathwaycom/pathway:latest
```

For cloud deployments, the command will vary depending on the cloud provider you use.
