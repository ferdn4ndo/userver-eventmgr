import logging
import os
import re
import time
from shutil import copyfile
from typing import Union, IO, Dict, List, Optional

from PIL import Image
from PIL.ExifTags import TAGS
from rawkit.options import WhiteBalance
from rawkit.raw import Raw

from stegano import exifHeader, lsbset
from stegano.lsbset import generators


def render_photo_from_cr2_raw_file(original_filename, dest_filename):
    with Raw(filename=original_filename) as raw:
        raw.options.white_balance = WhiteBalance(camera=False, auto=True)
        raw.save(filename=dest_filename)
    return True


def sign_image(signature: str, image_file_path: Union[str, IO[bytes]]):
    copied_file_path = "{}_{}.tmp".format(image_file_path, time.time())
    copyfile(image_file_path, copied_file_path)

    exifHeader.hide(input_image_file=copied_file_path, img_enc=image_file_path, secret_message=signature)
    os.remove(copied_file_path)

    secret_image = lsbset.hide(
        input_image=image_file_path,
        message=signature,
        generator=generators.fermat()
    )
    secret_image.save(image_file_path)


def get_sign_from_image(source_image: Union[str, IO[bytes]]) -> Dict:
    signature_from_exif = exifHeader.reveal(source_image)
    signature_from_data = lsbset.reveal("./image.png", generators.eratosthenes())

    return {
        'signature_from_data': signature_from_data,
        'signature_from_exif': signature_from_exif,
        'matched': signature_from_data is not None and signature_from_data == signature_from_data
    }


def get_image_exif(image_path: str) -> Dict:
    ret = {}
    image = Image.open(image_path)

    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            ret[decoded] = value

    ret['IMAGE_WIDTH'], ret['IMAGE_HEIGHT'] = image.size
    return ret


def parse_exif_string_to_list(original_string: str) -> Optional[List]:
    if not re.match(r"^\(\d+,\s*\d+\)$", str(original_string)):
        return None

    return str(original_string).replace(' ', '').replace('(', '').replace(')', '').split(',')


def get_exif_focal_length(exif_data: Dict) -> Optional[float]:
    if 'FocalLength' not in exif_data:
        return None

    data_parts = parse_exif_string_to_list(exif_data['FocalLength'])
    if data_parts is None:
        logging.warning('Unable to parse focal length: {}'.format(exif_data['FocalLength']))
        return None

    return float(data_parts[0]) / float(data_parts[1])


def get_exif_aperture(exif_data: Dict) -> Optional[str]:
    if 'FNumber' not in exif_data:
        return None

    data_parts = parse_exif_string_to_list(exif_data['FNumber'])
    if data_parts is None:
        logging.warning('Unable to parse aperture: {}'.format(exif_data['FNumber']))
        return None

    return 'f/{:.1f}'.format(float(data_parts[0]) / float(data_parts[1]))


def get_exif_exposition(exif_data: Dict) -> Optional[str]:
    if 'ExposureTime' not in exif_data:
        return None

    data_parts = parse_exif_string_to_list(exif_data['ExposureTime'])
    if data_parts is None:
        logging.warning('Unable to parse exposure time: {}'.format(exif_data['ExposureTime']))
        return None

    return '{}/{}'.format(data_parts[0], data_parts[1])


def get_exif_flash_fired(exif_data: Dict) -> Optional[bool]:
    """
    Parses the "flash" value from exif do determine if it was fired.

    Possible values:
    +-------------------------------------------------------+------+----------+-------+
    |                        Status                         | Hex  |  Binary  | Fired |
    +-------------------------------------------------------+------+----------+-------+
    | No Flash                                              | 0x0  | 00000000 | No    |
    | Fired                                                 | 0x1  | 00000001 | Yes   |
    | "Fired, Return not detected"                          | 0x5  | 00000101 | Yes   |
    | "Fired, Return detected"                              | 0x7  | 00000111 | Yes   |
    | "On, Did not fire"                                    | 0x8  | 00001000 | No    |
    | "On, Fired"                                           | 0x9  | 00001001 | Yes   |
    | "On, Return not detected"                             | 0xd  | 00001011 | Yes   |
    | "On, Return detected"                                 | 0xf  | 00001111 | Yes   |
    | "Off, Did not fire"                                   | 0x10 | 00010000 | No    |
    | "Off, Did not fire, Return not detected"              | 0x14 | 00010100 | No    |
    | "Auto, Did not fire"                                  | 0x18 | 00011000 | No    |
    | "Auto, Fired"                                         | 0x19 | 00011001 | Yes   |
    | "Auto, Fired, Return not detected"                    | 0x1d | 00011101 | Yes   |
    | "Auto, Fired, Return detected"                        | 0x1f | 00011111 | Yes   |
    |  No flash function                                    | 0x20 | 00100000 | No    |
    | "Off, No flash function"                              | 0x30 | 00110000 | No    |
    | "Fired, Red-eye reduction"                            | 0x41 | 01000001 | Yes   |
    | "Fired, Red-eye reduction, Return not detected"       | 0x45 | 01000101 | Yes   |
    | "Fired, Red-eye reduction, Return detected"           | 0x47 | 01000111 | Yes   |
    | "On, Red-eye reduction"                               | 0x49 | 01001001 | Yes   |
    | "On, Red-eye reduction, Return not detected"          | 0x4d | 01001101 | Yes   |
    | "On, Red-eye reduction, Return detected"              | 0x4f | 01001111 | Yes   |
    | "Off, Red-eye reduction"                              | 0x50 | 01010000 | No    |
    | "Auto, Did not fire, Red-eye reduction"               | 0x58 | 01011000 | No    |
    | "Auto, Fired, Red-eye reduction"                      | 0x59 | 01011001 | Yes   |
    | "Auto, Fired, Red-eye reduction, Return not detected" | 0x5d | 01011101 | Yes   |
    | "Auto, Fired, Red-eye reduction, Return detected"     | 0x5f | 01011111 | Yes   |
    +-------------------------------------------------------+------+----------+-------+

    :param exif_data:
    :return: If the flash was fired, or None if the exif information is not present
    """
    if 'Flash' not in exif_data:
        return None

    return bool((int(exif_data['Flash']) & 1) > 0)


def get_exif_orientation(exif_data: Dict) -> Optional[Dict]:
    """

    EXIF Value	Row #0 is:	    Column #0 is:

     +--------------+---------------------------------------+-------+----------+
    | EXIF Value    | Row #0 location   | Row #1 location   | Angle | Flipped  |
    +---------------+---------------------------------------+-------+----------+
    |      1        | Top               | Left side         |   0   |    NO    |
    |      2        | Top               | Right side        |   0   |   YES    |
    |      3        | Bottom            | Right side        |  180  |    NO    |
    |      4        | Bottom            | Left side         |  180  |   YES    |
    |      5        | Left side         | Top               |   90  |   YES    |
    |      6        | Right side        | Top               |   90  |    NO    |
    |      7        | Right side        | Bottom            |  270  |   YES    |
    |      8        | Left side         | Bottom            |  270  |    NO    |
    +---------------+---------------------------------------+-------+----------+

    :param exif_data:
    :return:
    """
    if 'Flash' not in exif_data:
        return None

    flash = int(exif_data['Flash'])

    return {
        'orientation_angle': 0 if flash in [0, 1] else 180 if flash in [3, 4] else 90 if flash in [5, 6] else 270,
        'is_flipped': True if flash in [2, 4, 5, 7] else False,
    }


def get_image_information(image_path: str):
    """Retrieves a dict of data about a given image file"""
    if not os.path.isfile(image_path):
        raise FileNotFoundError()

    exif_data = get_image_exif(image_path=image_path)

    return exif_data
