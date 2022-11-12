import logging
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
rekognition = boto3.client('rekognition')
bucket = "assignment2-nyu-photos"

openSearchHost = "search-assignment2-m3x5c4zswkalnoqpcpjqv47apm.us-east-1.es.amazonaws.com" 
openSearch = OpenSearch(
    hosts=[{"host": openSearchHost, "port": 443}],
    http_auth=("maxee998", "Admin1234!"),
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
)

s3 = boto3.resource('s3')

def print2(m):
    logger.debug(m)

def create(key, doc):
    response = openSearch.index(
        index = "photos",
        body=doc,
        refresh=True,
        id=key,
    )
    return response


def lambda_handler(event, context):
    # TODO implement
    
    file_key = event["Records"][0]["s3"]["object"]["key"]
    creation_time = event["Records"][0]["eventTime"]
    
    response = rekognition.detect_labels(
        Image={
            'S3Object': {
                'Bucket': bucket,
                'Name': file_key
            },
            
        },
        MinConfidence=70,
    )
    labels = [label["Name"] for label in response["Labels"]]
    photo = s3.Object(bucket, file_key)
    if "customlabels" in photo.metadata:
        for label in photo.metadata["customlabels"].split(","):
            labels.append(label.strip())
    doc = {
        "objectKey": file_key,
        "bucket": bucket,
        "createdTimestamp": creation_time,
        "labels": ";".join(labels),
    }

    return create(file_key, doc)