django-msgpackfield
===================

Provides a binary django model field with automatic serialization/deserialization
of native Python structures into/from [MsgPack](http://msgpack.org) format.

It also comes with a form widget, basically a `<TEXTAREA>` where data can be
input in JSON. This data is then converted to MsgPack when the form is submitted.

Requirements
------------

* Python3
* Django 1.8+
* Depends on package `msgpack`

Installation
------------

Install it with pip (or easy_install) :

    pip3 install django-msgpackfield

Usage
-----

Typical usage in a Django model:
```python
from django.db import models
from msgpackfield import MsgPackField

class MyModel ( models.Model ) :
    data = MsgPackField( null=True, blank=True )

obj = MyModel()
obj.data = { 'foo': 1, 'bar': 2, 'baz': [ 1, 2, 3, 4, 5 ] }
obj.save()
```

