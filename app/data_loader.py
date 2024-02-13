import boto3
from app.config import DATABASE_URL

BUCKET = 'phoneticsapibucket'

def download_data():
    s3 = boto3.client('s3')
    with open(DATABASE_URL, 'wb') as f:
        s3.download_fileobj(BUCKET, DATABASE_URL, f)
