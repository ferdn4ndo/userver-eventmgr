import time

from django.forms import model_to_dict

from core.models import StorageFile
from core.services.media.media_image_processor_service import MediaImageProcessorService
from core.services.message_broker.message_broker_service import MessageBrokerService


def process_media_image(storage_file: StorageFile):
    print("EXECUTING ASYNC TASK")

    processor = MediaImageProcessorService(storage_file=storage_file)
    processor.process()

    print("FILE PROCESSED")
    MessageBrokerService().send_message(
        topic='storage_file_processed',
        payload=model_to_dict(storage_file)
    )
