from html.parser import HTMLParser

class AttributeScanner(HTMLParser):

    def __init__(self, targ_attr: str):
        HTMLParser.__init__(self)
        
        if not isinstance(targ_attr, str):
            raise TypeError('targ_attr must be a string')

        self.targ_attr = targ_attr
        self.attr_values = list()

    def handle_starttag(self, tag, attrs):
        for attr, val in attrs:
            if attr == self.targ_attr:
                self.attr_values.append(val)

    def close(self):
        HTMLParser.close(self)
        return self.attr_values
