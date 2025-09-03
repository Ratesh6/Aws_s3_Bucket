import boto3

# ----------------------
# Configuration
# ----------------------
BUCKET_NAME = "my-test-bucket-730335282744"
OBJECT_NAME = "burger.jpg"

# ----------------------
# Initialize S3 client
# ----------------------
s3 = boto3.client("s3")

# ----------------------
# List all buckets
# ----------------------
print("Buckets in your account:")
buckets_resp = s3.list_buckets()
for bucket in buckets_resp["Buckets"]:
    print(f" - {bucket['Name']}")

# ----------------------
# Upload file (private)
# ----------------------
with open("./burger.jpg", "rb") as f:
    print(f"Uploading {f.name} to {BUCKET_NAME}...")
    s3.upload_fileobj(f, BUCKET_NAME, OBJECT_NAME)
print("Upload completed!")

# ----------------------
# Generate a pre-signed URL (valid for 1 hour)
# ----------------------
url = s3.generate_presigned_url(
    ClientMethod='get_object',
    Params={'Bucket': BUCKET_NAME, 'Key': OBJECT_NAME},
    ExpiresIn=3600  # 1 hour
)
print(f"Access your file via pre-signed URL (valid 1 hour):\n{url}")