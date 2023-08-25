from boto3.s3.transfer import TransferConfig


class AmazonS3TransferConfig(TransferConfig):
    """
    Configuration object for managed S3 transfers
    """

    def __init__(
        self,
        multipart_threshold=8 * 1024 * 1024,
        max_concurrency=10,
        multipart_chunksize=8 * 1024 * 1024,
        num_download_attempts=5,
        max_io_queue=100,
        io_chunksize=256 * 1024,
        use_threads=True
    ):
        super().__init__(
            multipart_threshold,
            max_concurrency,
            multipart_chunksize,
            num_download_attempts,
            max_io_queue,
            io_chunksize,
            use_threads
        )
