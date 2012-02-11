
from rstweaver  import WeaverLanguage
from subprocess import Popen, PIPE, STDOUT
import re
from uuid import uuid4
import operator

class Java(WeaverLanguage):
    
    def __init__(self, **other_options):
        WeaverLanguage.__init__(self, {
            WeaverLanguage.noninteractive: 'java'
        },
        **other_options
        )
    
    def test_compile(self, path, wd):
        proc = Popen(
            ['javac', path],
            stdout = PIPE,
            stderr = PIPE,
            cwd = wd
        )
        
        out, err = proc.communicate()
        
        return err + out
    
    def run(self, path, wd):
        proc = Popen(
            ['javac', path],
            stdout = PIPE,
            stderr = PIPE,
            cwd = wd
        )
        
        out, err = proc.communicate()
        status = proc.wait()
        
        if status != 0:
            return err + out
        
        proc = Popen(
            ['java', re.sub(r'\.java$', '', path)],
            stdout = PIPE,
            stderr = PIPE,
            cwd = wd
        )
        
        out, err = proc.communicate()
        
        return err + out
    
    def highlight_lang(self):
        return 'java'
    
    def extension(self):
        return '.java'


