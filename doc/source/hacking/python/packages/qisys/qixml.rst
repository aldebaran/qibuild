qixml module
============



.. automodule:: qisys.qixml


qisys.qixml.XMLParser
---------------------

.. autoclass:: XMLParser
   :members:

Example:

.. code-block:: xml

    <foo>
      <bar attr1="fooooooo">Some content!</bar>
      <easy><win>Yes!</win></easy>
      <win>Nooooooooooooooooooooooooooooooooo!</win>
    </foo>

Root of the XML is foo. When ``XMLParser.parse`` is called, it
will try to call ``_parse_TAGNAME`` where tag name is the actual name of the
tag you want to parse. It takes the element as a parameter.

You can call parse recursively (from ``_parse_TAGNAME`` functions) to parse
sub-trees. You always have ``backtrace`` to know from where you came
in ``_parse_TAGNAME``. Here is a complete example of a usage on XML above


.. code-block:: python

    class Foo(XMLParser):
        def _parse_bar(self, element):
            print 'Attribute attr1:', element.attrib['attr1']
            print 'Content:', element.text

        def _parse_easy(self, element):
            self.parse(element)

        def _parse_win(self, element):
            # We only want to parse win tag in easy tag.
            if 'easy' in self.backtrace:
                print 'Win text:', element.text

A parser class should not have an attribute with the name of an xml
attribute unless it wants to grab them.
