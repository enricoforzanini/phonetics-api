import boto3

BUCKET = 'phoneticsapibucket'
FILE = 'data.db'

def download_data():
    s3 = boto3.client('s3')
    with open(FILE, 'wb') as f:
        s3.download_fileobj(BUCKET, FILE, f)
  