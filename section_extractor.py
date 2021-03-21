from html.parser import HTMLParser
from os import path
from logging import Logger

class SectionExtractor(HTMLParser):

    ACCEPTED_EXT = {'.html', '.tmp'}

    def __init__(self, targ_tag: str, output_filename: str, logger: Logger = None):
        HTMLParser.__init__(self, convert_charrefs=False)
        
        if not isinstance(targ_tag, str):
            TypeError(f'*targ_tag* must be a string, not a {type(targ_tag)}!')
        if not isinstance(output_filename, str):
            raise TypeError(f'*output_filename* must be a string, not a {type(output_filename)}!')
        if logger is not None and not isinstance(logger, Logger):
            raise TypeError(f'*logger* must be None or a Logger, not a {type(logger)}!')
        if path.splitext(output_filename)[1] not in SectionExtractor.ACCEPTED_EXT:
            raise ValueError(f'*output_filename* must be a html file')

        self._read = False
        self.targ_tag = targ_tag
        self._output = open(output_filename, mode='wt')
        self.logger = logger

    def close(self):
        HTMLParser.close(self)
        self._output.close()

    def handle_starttag(self, tag, attrs):
        if self._read:
            if self.logger is not None:
                self.logger.debug(f'Extracting start tag {tag!r}')
            self._output.write(f'<{tag}')
            for attr, val in attrs:
                self._output.write(f' {attr}')
                if val != None:
                    self._output.write(f'="{val}"')
            self._output.write('>')
            
        if tag == self.targ_tag:
            if self.logger is not None:
                self.logger.debug(f'Found start tag matching target {self.targ_tag!r}')
            self._read = True

    def handle_endtag(self, tag):
        if tag == self.targ_tag:
            self._read = False
        if self._read:
            if self.logger is not None:
                self.logger.debug(f'Extracting end tag {tag!r}')
            self._output.write(f'</{tag}>')

    def handle_data(self, data):
        if self._read:
            if self.logger is not None:
                self.logger.debug(f'Extracting data {data!r}')
            self._output.write(data)

    def handle_entityref(self, ref):
        if self._read:
            if self.logger is not None:
                self.logger.debug(f'Extracting entity reference {ref!r}')
            self._output.write(f'&{ref};')

    def handle_charref(self, ref):
        if self._read:
            if self.logger is not None:
                self.logger.debug(f'Extracting character reference {ref!r}')
            self._output.write(f'&#{ref};')

    def handle_comment(self, comment):
        if self._read:
            if self.logger is not None:
                self.logger.debug(f'Extracting comment {comment!r}')
            self._ouput.write(f'<!--{comment}-->')

    def handle_decl(self, decl):
        if self.read:
            if self.logger is not None:
                self.logger.debug(f'Extracting declaration {decl!r}')
            self._output.write(f'<!{decl}>')

    def handle_pi(self, pi):
        if self._read:
            if self.logger is not None:
                self.logger.debug(f'Extracting processing instruction {pi!r}')
            self._output.write(f'<?{pi}>')
