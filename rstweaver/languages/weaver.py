
from rstweaver import WeaverLanguage
from subprocess import Popen, PIPE
from xml.sax.saxutils import escape
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
    
    def run(self, path, wd):
        command = ['rstweave', '--no-css', '-o', '-', path]
        run = Popen(
            command,
            stdout = PIPE,
            stderr = PIPE,
            cwd = wd
        )
        out, err = run.communicate()
        
        return err + out
 
    def run_get_block(self, path, wd, blockid):
        out = self.run(path, wd)
        
        start_code = 'START {0}'.format(blockid)
        stop_code = 'STOP {0}'.format(blockid)
        
        out = re.sub(r'.*{0}[^\>]*\>'.format(start_code), '', out,
            flags = re.MULTILINE | re.DOTALL)
        out = re.sub(r'\<[^\<]*{0}.*'.format(stop_code), '', out,
            flags = re.MULTILINE | re.DOTALL) 
        
        return out
    
    def annotate_block(self, code, blockid):
        anot_code = '\n\n.. START {0}\n\n{1}\n\n.. STOP {0}\n\n'.format(
            blockid, code
        )
 
        return anot_code
    
    def highlight(self, code):
        return escape(code)
    
    def html_prefix(self):
        return css
    
    def output_format(self):
        return 'html'
    
    def number_lines(self):
        return False

# Singleton
RstWeaverLanguage = RstWeaverLanguage()

css = '''
<style type="text/css">
.run-output-weaver {
    white-space: normal;
    font-family: ;
    background-color: ;
    border: 3px solid #eee;
    margin: 10px 0px 0px 0px;
    padding: 5px 10px 5px 10px;
}
.code-weaver {
    border: 3px solid #efe;
}
</style>
'''

