
from rstweaver import WeaverLanguage
from subprocess import Popen, PIPE
from xml.sax.saxutils import escape

class MinimalGHCI(WeaverLanguage):
    
    def __init__(self):
        WeaverLanguage.__init__(self, {
            WeaverLanguage.interactive:    'minghci'
        })
    
    def run_interactive(self, line, imports, wd):
        command = ['ghc'] + imports + ['-e', line]

        ghci = Popen(
            command,
            stdout = PIPE,
            stderr = PIPE,
            cwd = wd
        )
        
        out, err = ghci.communicate()

        return err + out
    
    def highlight(self, code):
        return escape(code)

# Singleton
MinimalGHCI = MinimalGHCI()

