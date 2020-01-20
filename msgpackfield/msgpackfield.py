"""
msgpackfield.py
~~~~~~~~~~~~~~~

Implements classes :class:`MsgPackField` and :class:`JsonTextWidget`.

:authors:
    Vasili Korol (https://github.com/vakorol)
"""

from logging import getLogger
from json import loads as json_loads, dumps as json_dumps
from json.decoder import JSONDecodeError
from msgpack import packb as msgpack_packb, unpackb as msgpack_unpackb
from django.db import models
from django.forms import CharField
from django.forms.widgets import Textarea

__all__ = ( 'MsgPackField', )

######################################################################
def _decodeMsgpack ( value ) :
    """Decodes unpacked Msgpack data.

    :param value:  The raw data from the database or the admin interface. \
    In the former case it is `bytes`, in the latter - `str`.

    :returns: Decoded native Python structure or `None`.
    :raises: None  Does not raise exceptions.
    """

    result = None

     # KLUDGE: value should not have type `str` here. But I couldn't make
     # msgpackfield work without this kludge - it seems that the value from
     # the widget is always `str`, while the value from the database is `bytes`.
    if type( value ) == str :
        try :
            result = json_loads( value )
        except ( TypeError, JSONDecodeError ) :
            getLogger( 'msgpackfield' ).warning( "Failed to decode data as JSON." )

     # If type of value is 'bytes' (expected behaviour)
    else :
        try:
            result = msgpack_unpackb( value, raw=False )
        except :
            try :
                result = msgpack_unpackb( value, raw=True )
            except :
                getLogger( 'msgpackfield' ).warning( "Failed to decode data as MsgPack." )

    return result


############################################################################
class JsonTextWidget ( Textarea ) :
    """A widget for editing data in JSON inside a `<TEXTAREA>`.
    """

    ######################################################################
    def render ( self, name, value, attrs=None, renderer=None ) :
        """Overrides parent method used to display data in the text area.

        The displayed data is formatted to prettified JSON.

        :raises: Exception  Various exceptions raised by :func:`json.dumps`.
        """

        value = json_dumps( value, indent="\t", separators=(', ', ': ') )
        return super( JsonTextWidget, self ).render( name, value, attrs, renderer )

    ######################################################################
    def value_from_datadict ( self, data, files, name ) :
        """Overrides parent method used to extract data from datadict \
        received from the client.

        :param data:    The submitted form data from the client.
        :param files:   The submitted files from the client (not used).
        :param name:    The name of the parameter in `data` containing a valid \
        JSON string.

        :raises:  KeyError  If failed to parse JSON string.
        """

        return data.get( name, None )


############################################################################
class MsgPackField ( models.Field ) :
    """A Django model field for storing data in MsgPack format in the database.

    The model field performs automatic serialization/deserialization of data \
    using binary MessagePack format.
    """

    ######################################################################
    def __init__ ( self, *args, **kwargs ) :
        kwargs['blank'] = True
        super( MsgPackField, self ).__init__( *args, **kwargs )

    ######################################################################
    def get_db_prep_value ( self, value, connection=None, prepared=False ) :
        """Overrides the parent method to encode data before storing it \
        in the database."""

        if not prepared :
            value = msgpack_packb( value )
        if value is not None :
            return connection.Database.Binary( value )
        return None

    ######################################################################
    def get_default(self):
        if self.has_default() and not callable(self.default):
            return self.default
        default = super( MsgPackField, self ).get_default()
        if default == '':
            return None
        return default

    ######################################################################
    def to_python ( self, value ) :
        return _decodeMsgpack( value )

    ######################################################################
    def from_db_value ( self, value, expression, connection, context=None ) :
        """Overrides the parent method to decode data into Python native \
        structure upon retrieval from the database.
        """
        return self.to_python( value )

    ######################################################################
    def get_prep_value ( self, value ) :
        return self.to_python( value )

    ######################################################################
    def value_to_string ( self, obj ) :
        if hasattr(self, '_get_val_from_obj'):
            value = self._get_val_from_obj(obj)
        else:
            value = super( MsgPackField, self ).value_from_object(obj)
        return json_dumps( value, indent="\t", separators=(', ', ': ') )

    ######################################################################
    def formfield ( self, **kwargs ):
        defaults = { 'widget': JsonTextWidget, 'help_text': self.help_text }
        defaults.update( kwargs )
        return CharField( **defaults )

    ######################################################################
    def get_internal_type ( self ) :
        return "BinaryField"

