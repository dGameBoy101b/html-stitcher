from html.parser import HTMLParser
from os import path

class SectionExtractor(HTMLParser):

    ACCEPTED_EXT = {'.html', '.tmp'}

    def __init__(self, targ_tag: str, output_filename: str):
        HTMLParser.__init__(self, convert_charrefs=False)
        
        if not isinstance(targ_tag, str):
            TypeError('targ_tag must be a string')
        if not isinstance(output_filename, str):
            raise TypeError('output_filename must be a string')
        if path.splitext(output_filename)[1] not in SectionExtractor.ACCEPTED_EXT:
            raise ValueError('output_filename must be a html file')

        self._read = False
        self.targ_tag = targ_tag
        self._output = open(output_filename, mode='wt')

    def close(self):
        HTMLParser.close(self)
        self._output.close()

    def handle_starttag(self, tag, attrs):
        if self._read:
            self._output.write(f'<{tag}')
            for attr, val in attrs:
                self._output.write(f' {attr}')
                if val != None:
                    self._output.write(f'="{val}"')
            self._output.write('>')
        if tag == self.targ_tag:
            self._read = True

    def handle_endtag(self, tag):
        if tag == self.targ_tag:
            self._read = False
        if self._read:
            self._output.write(f'</{tag}>')

    def handle_data(self, data):
        if self._read:
            self._output.write(data)

    def handle_entityref(self, ref):
        if self._read:
            self._output.write(f'&{ref};')

    def handle_charref(self, ref):
        if self._read:
            self._output.write(f'&#{ref};')

    def handle_comment(self, comment):
        if self._read:
            self._ouput.write(f'<!--{comment}-->')

    def handle_decl(self, decl):
        if self.read:
            self._output.write(f'<!{decl}>')

    def handle_pi(self, pi):
        if self._read:
            self._output.write(f'<?{pi}>')
