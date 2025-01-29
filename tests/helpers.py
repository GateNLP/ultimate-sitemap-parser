import gzip as gzip_lib
from typing import Union


def gzip(data: Union[str, bytes]) -> bytes:
    """Gzip data."""

    if data is None:
        raise Exception("Data is None.")

    if isinstance(data, str):
        data = data.encode("utf-8")

    if not isinstance(data, bytes):
        raise Exception(f"Data is not str or bytes: {str(data)}")

    try:
        gzipped_data = gzip_lib.compress(data, compresslevel=9)
    except Exception as ex:
        raise Exception(f"Unable to gzip data: {str(ex)}")

    if gzipped_data is None:
        raise Exception("Gzipped data is None.")

    if not isinstance(gzipped_data, bytes):
        raise Exception("Gzipped data is not bytes.")

    return gzipped_data
