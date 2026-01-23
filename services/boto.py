import boto3

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