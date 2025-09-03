import boto3
import requests
import os
import json
from datetime import datetime, timezone
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import sys

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = os.getenv("CITY", "Delhi")
BUCKET_NAME = os.getenv("BUCKET_NAME", "weather-data-ratesh-001")
REGION = os.getenv("AWS_REGION", "us-east-1")

if not API_KEY:
    print("Missing OPENWEATHER_API_KEY in .env file")
    sys.exit(1)

# -----------------------------
# Initialize S3 client
# -----------------------------
s3 = boto3.client("s3", region_name=REGION)


# -----------------------------
# Ensure bucket exists
# -----------------------------
def ensure_bucket(bucket_name):
    """Check if S3 bucket exists, create if not (with encryption & restricted access)."""
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} exists, reusing it.")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code in ("404", "NoSuchBucket"):
            print(f"Bucket {bucket_name} not found. Creating...")
            if REGION == "us-east-1":
                s3.create_bucket(Bucket=bucket_name)
            else:
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": REGION}
                )

            # Block public access
            s3.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    "BlockPublicAcls": True,
                    "IgnorePublicAcls": True,
                    "BlockPublicPolicy": True,
                    "RestrictPublicBuckets": True,
                },
            )

            # Enable encryption
            s3.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={
                    "Rules": [
                        {"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}
                    ]
                },
            )

            print(f"Bucket {bucket_name} created in {REGION} with encryption and blocked public access.")
        else:
            print(f"Error checking bucket: {e}")
            sys.exit(1)


# -----------------------------
# Fetch weather data
# -----------------------------
def fetch_weather():
    """Fetch current weather data from OpenWeather API."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        print(f"Weather data fetched for {CITY}")
        return resp.json()
    except requests.RequestException as e:
        print(f"Failed to fetch weather data: {e}")
        sys.exit(1)


# -----------------------------
# Upload data to S3
# -----------------------------
def upload_to_s3(data):
    """Save weather data locally and upload to S3."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    key = f"raw/{datetime.now().strftime('%Y/%m/%d')}/{CITY}/{CITY}_{timestamp}.json"
    filename = f"{CITY}_{timestamp}.json"

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

    try:
        s3.upload_file(filename, BUCKET_NAME, key)
        print(f"Uploaded {filename} → s3://{BUCKET_NAME}/{key}")
    except ClientError as e:
        print(f"Failed to upload to S3: {e}")
        sys.exit(1)

    # Generate pre-signed URL
    try:
        presigned_url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': key},
            ExpiresIn=3600  # 1 hour
        )
        print(f"Access your file via pre-signed URL (1 hour):\n{presigned_url}")
    except ClientError as e:
        print(f"Failed to generate pre-signed URL: {e}")

    return filename


# -----------------------------
# Save bucket ACL to JSON
# -----------------------------
def save_bucket_acl(bucket_name):
    """Retrieve bucket ACL and save to local JSON file."""
    try:
        acl = s3.get_bucket_acl(Bucket=bucket_name)
        acl_filename = f"{bucket_name}_acl.json"
        with open(acl_filename, "w") as f:
            json.dump(acl, f, indent=4)
        print(f"Bucket ACL saved to {acl_filename}")
    except ClientError as e:
        print(f"Failed to get bucket ACL: {e}")


# -----------------------------
# Main execution
# -----------------------------
if __name__ == "__main__":
    ensure_bucket(BUCKET_NAME)
    weather_data = fetch_weather()
    upload_to_s3(weather_data)
    save_bucket_acl(BUCKET_NAME)
