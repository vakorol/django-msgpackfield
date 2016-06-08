from __future__  import absolute_import

try:
    VERSION = __import__('pkg_resources') \
        .get_distribution('django-msgpackfield').version
except Exception:
    VERSION = 'unknown'

from .msgpackfield import MsgPackField
