import logging
from boto3 import resource
from boto3.s3.transfer import S3Transfer
from botocore.exceptions import ClientError

from core.models import StorageFile
from core.services.storage_drivers.amazon_s3_transfer_config import AmazonS3TransferConfig
from core.services.storage_drivers.generic_storage_driver import GenericStorageDriver
from core.services.web_request.web_request_service import WebRequestService


class AmazonS3StorageDriver(GenericStorageDriver):
    """
    Storage driver class for Amazon S3
    """
    DEFAULT_ROOT_FOLDER: str = ''


    def get_remote_root_path(self) -> str:
        """
        Returns the remote root path. Should be implemented for each storage.
        :return: The root path
        """
        if 'AWS_S3_ROOT_FOLDER' not in self.storage.credentials:
            return self.DEFAULT_ROOT_FOLDER

        return self.storage.credentials['AWS_S3_ROOT_FOLDER']

    def perform_upload_from_path(self, local_path: str, remote_path: str):
        """
        Upload a file from a local path
        :param local_path: the local path of the file that's going to be uploaded
        :param remote_path: the remote path to where the file should be uploaded
        """
        s3 = self.get_s3_resource()
        transfer = S3Transfer(client=s3.meta.client, config=AmazonS3TransferConfig())
        transfer.upload_file(
            filename=local_path,
            bucket=self.storage.credentials['AWS_S3_BUCKET'],
            key=remote_path
        )

    def perform_upload_from_url(self, url: str, remote_path: str):
        """
        Upload a file from a given url (without downloading it to the container)
        :param url: the url of the file that's going to be uploaded
        :param remote_path: the remote path to where the file should be uploaded
        """
        s3 = self.get_s3_resource()

        # Given an Internet-accessible URL, download the image and upload it to S3,
        # without needing to persist the image to disk locally
        req_for_image = WebRequestService(url=url, stream=True)
        file_object_from_req = req_for_image.get_raw()
        req_data = file_object_from_req.read()

        # Do the actual upload to s3
        s3.meta.client.put_object(
            Bucket=self.storage.credentials['AWS_S3_BUCKET'],
            Key=remote_path,
            Body=req_data
        )

    def perform_download_to_path(self, remote_path: str, local_dest: str):
        """
        Download a file from the remote storage
        :param remote_path: the remote path of the file that should be downloaded
        :param local_dest: the destination file path
        :return:
        """
        s3 = self.get_s3_resource()
        transfer = S3Transfer(client=s3.meta.client, config=AmazonS3TransferConfig())
        transfer.download_file(
            bucket=self.storage.credentials['AWS_S3_BUCKET'],
            key=remote_path,
            filename=local_dest,
        )

    def generate_download_url(self, file: StorageFile, expiration_seconds: int = 3600, force_download: bool = False) -> str:
        """
        Generate a presigned URL to share an S3 object from a StorageFile
        :param file: The StorageFile model to be downloaded
        :param force_download: if the file download should be enforced (not rendered)
        :param expiration_seconds: Time in seconds for the presigned URL to remain valid
        :return:
        """
        s3 = self.get_s3_resource()

        params = {
            'Bucket': self.storage.credentials['AWS_S3_BUCKET'],
            'Key': file.real_path,
            'ResponseContentDisposition': "{};filename={}".format(
                'inline' if not force_download else 'attachment',
                file.get_filename_from_virtual_path()
            )
        }

        if file.type is not None:
            params['ResponseContentType'] = file.type.mime_type

        try:
            url = s3.meta.client.generate_presigned_url('get_object', Params=params, ExpiresIn=expiration_seconds)

        except ClientError as e:
            logging.error(e)
            return None

        return str(url)

    def perform_delete(self, file: StorageFile):
        """
        Performs the remote file deletion given a StorageFile. Implement this method with the storage logic.
        :param file: the StorageFile model to be deleted
        :return:
        """
        s3 = self.get_s3_resource()
        try:
            s3.Bucket(self.storage.credentials['AWS_S3_BUCKET']).Object(self.get_real_remote_path(file)).delete()
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            else:
                # Something else has gone wrong.
                raise

    def remote_file_exists(self, file: StorageFile) -> bool:
        """
        Determines if a given real remote path exists
        :param file: the file to check whether its remote path exists
        :return: boolean indicating if the file exists or not
        """
        s3 = self.get_s3_resource()
        try:
            s3.Bucket(self.storage.credentials['AWS_S3_BUCKET']).Object(self.get_real_remote_path(file)).load()
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            else:
                # Something else has gone wrong.
                raise
        else:
            return True

    def get_s3_resource(self):
        """
        Retrieves a valid boto S3 resource
        :return:
        """
        s3 = resource(
            service_name='s3',
            region_name=self.storage.credentials['AWS_S3_REGION'],
            aws_access_key_id=self.storage.credentials['AWS_S3_ID'],
            aws_secret_access_key=self.storage.credentials['AWS_S3_KEY'],
        )

        found = False
        for bucket in s3.buckets.all():
            if bucket.name == self.storage.credentials['AWS_S3_BUCKET']:
                found = True

        if not found:
            logging.error('Not seeing the s3 bucket (permissions in IAM?)')

        return s3
