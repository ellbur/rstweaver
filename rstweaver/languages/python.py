
from rstweaver  import WeaverLanguage
from subprocess import Popen, PIPE, STDOUT
import re
from uuid import uuid4
import operator

class Python(WeaverLanguage):
    
    def __init__(self):
        WeaverLanguage.__init__(self, {
            WeaverLanguage.noninteractive: 'python',
            WeaverLanguage.interactive:    'ipython'
        })
    
    def test_compile(self, path, wd):
        proc = Popen(
            ['python', path],
            stdout = PIPE,
            stderr = PIPE,
            cwd = wd
        )
        
        out, err = proc.communicate()
        
        return err
    
    def run(self, path, wd):
        proc = Popen(
            ['python', path],
            stdout = PIPE,
            stderr = PIPE,
            cwd = wd
        )
        
        out, err = proc.communicate()
        
        return err + out
    
    def run_interactive(self, lines, imports, wd):
        return self.chopped_interactive(
            lines,
            lambda id: "'%s'\n" % id,
            lambda id: "'%s'" % id,
            reduce(operator.add, [
                '%%run -i %s\n' % im for im in imports
            ], ''),
            lambda line: line,
            ['ipython', '-quick', '-prompt_in1', '\n', '-prompt_out', '\n'],
            wd
        )
    
    def highlight_lang(self):
        return 'python'
    
    def extension(self):
        return '.py'
    
    def interactive_prompt(self):
        return 'py> '

Python = Python()

