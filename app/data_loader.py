import boto3
import json

bucket_name = 'phoneticsapibucket'
translations = {}

def load_translations() -> dict:
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    files = list(bucket.objects.all())
    for file in files:
        file_name = file.key.split('.')[0]
        response = file.get()['Body']
        json_string = response.read().decode('utf-8')
        translations[file_name] = json.loads(json_string)
    return translations
