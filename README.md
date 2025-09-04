**Weather Data → S3 Ingestion Script**

This project fetches current weather data from the OpenWeatherMap API and stores it in an Amazon S3 bucket. The script is idempotent – it creates the bucket if not present, or reuses it otherwise. Each run uploads a new timestamped JSON file.

** Features**

Automatic S3 bucket creation with:

Blocked Public Access

Default Server-Side Encryption (SSE-S3)

Timestamped JSON uploads for each execution

Retry mechanism for transient API/network errors

No hardcoded secrets → uses environment variables

** Prerequisites**

Install dependencies:

pip install boto3 requests python-dotenv


Configure AWS CLI:

aws configure


Provide:

AWS Access Key ID

AWS Secret Access Key

Default region (e.g., us-east-1)

Output format (json)

Verify AWS setup:

aws sts get-caller-identity
aws s3 ls


Required IAM permissions:

s3:CreateBucket

s3:GetBucketLocation

s3:ListAllMyBuckets

s3:ListBucket

s3:PutObject

** Usage**

Run the script:

python weather_ingest.py


First Run → Creates bucket weather-data-<yourname> and uploads JSON.

Subsequent Runs → Reuses bucket and adds new timestamped JSON files.

**Deliverables**

weather.py → Python script

README.md → Documentation

S3 bucket screenshots/listings with multiple JSON uploads

