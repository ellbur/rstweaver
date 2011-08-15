
from rstweaver import WeaverLanguage
from subprocess import Popen, PIPE, STDOUT

class Happy(WeaverLanguage):
    
    def __init__(self, **other_options):
        WeaverLanguage.__init__(self, {
            WeaverLanguage.noninteractive: 'happy'
        },
        **other_options
        )
    
    def run(self, path, wd):
        runghc = Popen(
            ['happy', path],
            stdout = PIPE,
            stderr = PIPE,
            cwd = wd
        )
        
        out, err = runghc.communicate()
        
        return err + out
    
    def highlight_lang(self):
        return 'haskell'
    
