import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

from .fetch import *  # noqa: E402
from .utils import *  # noqa: E402
