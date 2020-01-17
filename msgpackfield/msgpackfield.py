############################################################################
#   @file   msgpackfield.py
#   @brief  Defines classes `MsgPackField` and `JsonTextWidget`.
#   @author  V.Korol
############################################################################

import json
from msgpack import packb as msgpackEncode, unpackb as msgpackDecode
from django.db import models
from django.forms import CharField
from django.forms.widgets import Textarea

######################################################################
#   @brief  A clutch used to properly decode data for the messagepack field.
#   @param  value   The raw data received from the database or the admin
#   interface. In the former case it is `bytes`, in the latter - `str`.
#   @returns    Decoded native Python structure or `None`.
#   @throws     Does not raise exceptions.
######################################################################
def _decodeMsgpack ( value ) :

    result = None

     # CLUTCH: value should not have type `str` here. But I couldn't make
     # msgpackfield work without this clutch - it seems that the value from
     # the widget is always `str`, while the value from the database is `bytes`.
    if type( value ) == str :
        try :
            result = json.loads( value )
        except :
            pass

     # If type of value is 'bytes' (expected behaviour)
    else :
        try:
            result = msgpackDecode( value, encoding="utf-8" )
        except :
            try :
                result = msgpackDecode( value )
            except :
                pass

    return result


############################################################################
#   @brief  A widget for editing data in JSON inside a `<TEXTAREA>`.
############################################################################
class JsonTextWidget ( Textarea ) :

    ######################################################################
    #   @brief  Overrides parent method used to display data in the text area.
    #
    #   The displayed data is formatted to prettified JSON.
    ######################################################################
    def render ( self, name, value, attrs=None, renderer=None ) :
        value = json.dumps( value, indent="\t", separators=(', ', ': ') )
        return super( JsonTextWidget, self ).render( name, value, attrs )

    ######################################################################
    #   @brief  Overrides parent method used to extract data from datadict
    #   received from the client.
    #   @param  data    The submitted form data from the client.
    #   @param  files   The submitted files from the client.
    #   @param  name    The name of the parameter in `data` containing a valid
    #   JSON string.
    #   @throws `ValueError` if failed to parse JSON string.
    ######################################################################
    def value_from_datadict ( self, data, files, name ) :
        string = data.get( name, None )
        return string


############################################################################
#   @brief  A Django model field for storing data in MsgPack format in the
#   database.
#
#   This model field does automatic serialization/deserialization of data
#   using binary MessagePack format.
############################################################################
class MsgPackField ( models.Field ) :

    ######################################################################
    ######################################################################
    def __init__ ( self, *args, **kwargs ) :
        kwargs['blank'] = True
        super( MsgPackField, self ).__init__( *args, **kwargs )

    ######################################################################
    #   @brief  Overload of parent method to encode data before storing
    #   it in the database.
    ######################################################################
    def get_db_prep_value ( self, value, connection=None, prepared=False ) :
        if not prepared :
            value = msgpackEncode( value )
        if value is not None :
            return connection.Database.Binary( value )
        return value


    ######################################################################
    ######################################################################
    def get_default(self):
        if self.has_default() and not callable(self.default):
            return self.default
        default = super( MsgPackField, self ).get_default()
        if default == '':
            return None
        return default


    ######################################################################
    ######################################################################
    def to_python ( self, value ) :
        return _decodeMsgpack( value )

    ######################################################################
    #   @brief  Overload of parent method to decode data into Python native
    #   structure upon retrieval from the database.
    ######################################################################
    def from_db_value ( self, value, expression, connection, context=None ) :
        return self.to_python( value )


    ######################################################################
    ######################################################################
    def get_prep_value ( self, value ) :
        return self.to_python( value )


    ######################################################################
    ######################################################################
    def value_to_string ( self, obj ) :
        if hasattr(self, '_get_val_from_obj'):
            value = self._get_val_from_obj(obj)
        else:
            value = super( MsgPackField, self ).value_from_object(obj)
        return json.dumps( value, indent="\t", separators=(', ', ': ') )


    ######################################################################
    ######################################################################
    def formfield ( self, **kwargs ):
        defaults = { 'widget': JsonTextWidget }
        defaults.update( kwargs )
        return CharField( **defaults )


    ######################################################################
    ######################################################################
    def get_internal_type ( self ) :
        return "BinaryField"

