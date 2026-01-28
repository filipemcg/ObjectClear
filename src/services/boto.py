import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

def encode_dict_to_dynamodb_map(data: dict):
    serializer = TypeSerializer()
    return {k: serializer.serialize(v) for k, v in data.items()}


def decode_dynamodb_map_to_dict(dynamodb_map: dict):
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in dynamodb_map.items()}


class JobStatusDynamo:
    def __init__(self):
        self.client = boto3.client("dynamodb", region_name="eu-west-1")  # type: ignore
        self.table = "vc-job-status"
        self.region = "eu-west-1"

    def put_item(self, hash: str, range: str, meta: dict):
        meta = encode_dict_to_dynamodb_map(meta)
        self.client.put_item(
            TableName=self.table,
            Item={
                "hash": {"S": hash},
                "range": {"S": range},
                "meta": {"M": meta},
            },
        )


class S3:
    def __init__(self, bucket: str) -> None:
        self.__s3 = boto3.client("s3")  # type: ignore
        self.__bucket = bucket

    def upload_file(self, src_path: str, dest_path: str):
        self.__s3.upload_file(src_path, self.__bucket, dest_path)

    def upload_object(self, dest_path, data):
        self.__s3.put_object(Bucket=self.__bucket, Key=dest_path, Body=data)

    def get_object(self, path) -> bytes:
        response = self.__s3.get_object(Bucket=self.__bucket, Key=path)
        data = response["Body"].read()
        return data

    def delete_object(self, path):
        self.__s3.delete_object(Bucket=self.__bucket, Key=path)