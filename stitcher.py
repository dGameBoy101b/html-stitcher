from html.parser import HTMLParser
from os import path
from attribute_scanner import AttributeScanner
from section_extractor import SectionExtractor
from logging import Logger

class Stitcher(HTMLParser):

    INSERT_ATTR = 'py-stitch'
    VALID_EXT = {'.html'}
    TEMP_EXT = '.tmp'
    FAIL_COMMENT = '<!--failed to load {0}-->'
    HEAD_TAG = 'head'
    HEAD_FILE_SUFFIX = '_head.tmp'
    BODY_TAG = 'body'
    BODY_FILE_SUFFIX = '_body.tmp'

    def __init__(self, base_dir: str, template_filename: str, output_filename: str, passes: int = -1, logger: Logger = None):
        HTMLParser.__init__(self, convert_charrefs=False)
        
        if not isinstance(base_dir, str):
            raise TypeError(f'*base_dir* must be a string, not a {type(template_filename)}!')
        if not isinstance(template_filename, str):
            raise TypeError(f'*template_filename* must be a string, not a {type(template_filename)}!')
        if not isinstance(output_filename, str):
            raise TypeError(f'*output_filename* must be a string, not a {type(output_filename)}!')
        if not isinstance(passes, int):
            raise TypeError(f'*passes* must be an integer, not {type(passes)}!')
        if logger is not None and not isinstance(logger, Logger):
            raise TypeError(f'*logger* must be a Logger, not a {type(logger)}!')
        if path.splitext(template_filename)[1] not in Stitcher.VALID_EXT:
            raise ValueError('*template_filename* must be a html file')
        if path.splitext(output_filename)[1] not in Stitcher.VALID_EXT:
            raise ValueError('*output_filename* must be a html file')
        if passes < -1 or passes == 0:
            raise ValueError('*passes* must be -1 or greater than 0')
        if not path.isdir(base_dir):
            raise ValueError('*base_dir* must be an existing directory')
        if not path.isfile(path.join(base_dir, template_filename)):
            raise ValueError('*template_filename* must be an existing file in *base_dir*')

        self.logger = logger
        
        #calculate filenames
        in_filename = path.join(base_dir, template_filename)
        temp_filename = path.join(base_dir, path.splitext(output_filename)[0] + Stitcher.TEMP_EXT)
        out_filename = path.join(base_dir, output_filename)
        
        #copy input to temporary input
        in_file = open(in_filename, mode='rt')
        temp_file = open(temp_filename, mode='wt')
        temp_file.write(in_file.read())
        temp_file.close()
        in_file.close()

        #set additional instance variables
        self._base_dir = base_dir
        
        while True:
            #extract insertion points
            in_file = open(temp_filename, mode='rt')
            scanner = AttributeScanner(Stitcher.INSERT_ATTR)
            scanner.feed(in_file.read())
            self._inserts = set(scanner.close())
            in_file.close()

            #loop condition
            if passes == 0 or len(self._inserts) < 1:
                break
            
            #extract insert heads and bodies
            for file in self._inserts:
                #calculate filenames
                filename = path.join(base_dir, file)
                head_filename = path.join(base_dir, path.splitext(file)[0] + Stitcher.HEAD_FILE_SUFFIX)
                body_filename = path.join(base_dir, path.splitext(file)[0] + Stitcher.BODY_FILE_SUFFIX)

                #open head and body files
                head_file = open(head_filename, mode='wt')
                body_file = open(body_filename, mode='wt')
                
                if path.splitext(file)[1] not in Stitcher.VALID_EXT or not path.isfile(filename):
                    #record failure
                    if self.logger is not None:
                        self.logger.warning(f'Failed to load {file}')
                    head_file.close()
                    body_file.write(Stitcher.FAIL_COMMENT.format(file))
                    body_file.close()
                    
                else:
                    #extract head
                    head_file.close()
                    extractor = SectionExtractor(Stitcher.HEAD_TAG, head_filename, self.logger)
                    insert_file = open(filename, mode='rt')
                    extractor.feed(insert_file.read())
                    insert_file.close()
                    extractor.close()
                    
                    #extract body
                    body_file.close()
                    extractor = SectionExtractor(Stitcher.BODY_TAG, body_filename, self.logger)
                    insert_file = open(filename, mode='rt')
                    extractor.feed(insert_file.read())
                    extractor.close()
                    insert_file.close()
                    
            #make insertions
            in_file = open(temp_filename, mode='rt')
            self._output = open(out_filename, mode='wt')
            self.feed(in_file.read())
            in_file.close()
            self.close()
            self._output.close()
            
            #report pass count
            if self.logger is not None:
                self.logger.info(f'Pass {passes} complete')
            passes -= 1
            
            #copy output to temporary input
            out_file = open(out_filename, mode='rt')
            temp_file = open(temp_filename, mode='wt')
            temp_file.write(out_file.read())
            temp_file.close()
            out_file.close()

        del self

    def handle_starttag(self, tag, attrs):
        #write start tag
        self._output.write(f'<{tag}')
        if self.logger is not None:
            self.logger.debug(f'Start tag {tag!r} encountered')
        for k, v in attrs:
            if v is None:
                if self.logger is not None:
                    self.logger.debug(f'Name only attribute {k!r} encountered')
                self._output.write(f' {k}')
            elif k == Stitcher.INSERT_ATTR:
                if self.logger is not None:
                    self.logger.info(f'Substitution for {v!r} encountered')
            else:
                if self.logger is not None:
                    self.logger.debug(f'Attribute {k!r} with value {v!r} encountered')
                self._output.write(f' {k}="{v}"')
        self._output.write('>')
        
        #add all head insertions
        if tag == Stitcher.HEAD_TAG:
            if self.logger is not None:
                self.logger.info('Head tag encountered')
            for file in self._inserts:
                if self.logger is not None:
                    self.logger.info(f'Inserting {file} in head')
                insert_head = open(path.join(self._base_dir, path.splitext(file)[0] + Stitcher.HEAD_FILE_SUFFIX), mode='rt')
                self._output.write(insert_head.read())
                insert_head.close()

        #add body insertions
        for file in self._inserts:
            if (Stitcher.INSERT_ATTR, file) in attrs:
                if self.logger is not None:
                    self.logger.info(f'Inserting {file} in body')
                insert_body = open(path.join(self._base_dir, path.splitext(file)[0] + Stitcher.BODY_FILE_SUFFIX), mode='rt')
                self._output.write(insert_body.read())
                insert_body.close()

    def handle_endtag(self, tag):
        #write end tag
        if self.logger is not None:
            self.logger.debug(f'End tag {tag!r} encountered')
        self._output.write(f'</{tag}>')

    def handle_data(self, data):
        #write data
        if self.logger is not None:
            self.logger.debug(f'Data {data!r} encountered')
        self._output.write(f'{data}')

    def handle_entityref(self, ref):
        #write entity reference
        if self.logger is not None:
            self.logger.debug(f'Entity reference {ref!r} encountered')
        self._output.write(f'&{ref};')

    def handle_charref(self, ref):
        #write character reference
        if self.logger is not None:
                self.logger.debug(f'character reference {ref!r} encountered')
        self._output.write(f'&#{ref};')

    def handle_comment(self, comment):
        #write comment
        if self.logger is not None:
            self.logger.debug(f'Comment {comment!r} encountered')
        self._output.write(f'<!--{comment}-->')

    def handle_decl(self, decl):
        #write declaration
        if self.logger is not None:
            self.logger.debug(f'Declaration {decl!r} encountered')
        self._output.write(f'<!{decl}>')

    def handle_pi(self, pi):
        #write processing instruction
        if self.logger is not None:
            self.logger.debug(f'Processing instruction {pi!r} encountered')
        self._output.write(f'<?{pi}>')
