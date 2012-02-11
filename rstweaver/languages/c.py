
from rstweaver  import WeaverLanguage
from subprocess import Popen, PIPE, STDOUT
import re
from uuid import uuid4
import operator

class C(WeaverLanguage):
    
    def __init__(self, **other_options):
        WeaverLanguage.__init__(self, {
            WeaverLanguage.noninteractive: 'c'
        },
        **other_options
        )
    
    def test_compile(self, path, wd):
        proc = Popen(
            ['gcc', '-c', '-o', '/dev/null', path],
            stdout = PIPE,
            stderr = PIPE,
            cwd = wd
        )
        
        out, err = proc.communicate()
        
        return err + out
    
    def run(self, path, wd):
        proc = Popen(
            ['gcc', '-o', 'main', path],
            stdout = PIPE,
            stderr = PIPE,
            cwd = wd
        )
        
        out, err = proc.communicate()
        status = proc.wait()
        
        if status != 0:
            return err + out
        
        proc = Popen(
            ['./main'],
            stdout = PIPE,
            stderr = PIPE,
            cwd = wd
        )
        
        out, err = proc.communicate()
        
        return err + out
    
    def highlight_lang(self):
        return 'c'
    
    def extension(self):
        return '.c'

