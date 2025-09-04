Weather Data → S3 Ingestion Script
**** Overview****

This project fetches current weather data from the OpenWeatherMap API
 and stores it in an Amazon S3 bucket.
The script is idempotent:

If the S3 bucket exists → it reuses it.

If not → it creates it automatically with encryption enabled and public access blocked.

Each run generates a new timestamped JSON file uploaded to the S3 bucket.
 **Features**

Automated bucket creation with proper configuration:

Block Public Access

Default Encryption (SSE-S3)

Timestamped JSON uploads for each execution.
** Prerequisites**
1. Install Dependencies
pip install boto3 requests python-dotenv

2. AWS Setup

Configure your AWS CLI:

aws configure


Provide:

AWS Access Key ID

AWS Secret Access Key

Default region name (e.g., us-east-1)

Output format (json recommended)

Test your configuration:

aws sts get-caller-identity
aws s3 ls


Ensure your IAM user has these permissions:

s3:CreateBucket

s3:GetBucketLocation

s3:ListAllMyBuckets

s3:ListBucket

s3:PutObject

Retry mechanism for transient API/network errors.

No hardcoding of credentials or API keys (uses environment variables).
**Usage**

Run the script:

python weather_ingest.py


On first run:

A new bucket will be created with the naming convention:

weather-data-ratesh-001


Weather JSON will be uploaded.

On subsequent runs:

Bucket is reused.

New JSON files are added.
 **Deliverables**

Python Script: weather.py

README.md: (this file)

S3 Bucket Screenshot/Listing showing multiple JSON uploads.
