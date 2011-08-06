
from rstweaver import WeaverLanguage
import docutils.core
from docutils import nodes
from subprocess import Popen, PIPE
import re

class RstWeaverLanguage(WeaverLanguage):
    
    def __init__(self):
        WeaverLanguage.__init__(self, {
            WeaverLanguage.noninteractive: 'weaver'
        })
    
    def test_compile(self, path, wd):
        run = Popen(
            ['rstweave', '-o', '/dev/null', path],
            stdout = PIPE,
            stderr = PIPE,
            cwd = wd
        )
        out, err = run.communicate()
        
        return err
    
    def run_tokens(self, path, wd):
        with open(wd + '/' + path, 'r') as hl:
            content = hl.read()
        tree = docutils.core.publish_doctree(content)
        return tree.children
    
    def format_tokens(self, tokens):
        root = nodes.block_quote(
            classes=['run-output', 'run-output-weaver'],
            ids=['weaver']
        )
        root += nodes.inline('', '')
        for c in tokens:
            root += c
        return root
    
    def run(self, path, wd):
        return self.format_tokens(self.run_tokens(path, wd))
    
    def highlight_lang(self):
        return 'rst'
    
    def extension(self):
        return '.rst'
    
    def css(self):
        return css
    
    def number_lines(self):
        return False

# Singleton
RstWeaverLanguage = RstWeaverLanguage()

css = '''
.run-output-weaver {
    white-space: normal;
    font-family: default;
    background-color: ;
    border: 3px solid #eee;
    margin: 10px 0px 0px 0px;
    padding: 5px 10px 5px 10px;
}
.code-weaver {
    border: 3px solid #efe;
}
'''

