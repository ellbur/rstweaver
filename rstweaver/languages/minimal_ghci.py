
from rstweaver import WeaverLanguage
from subprocess import Popen, PIPE

class MinimalGHCI(WeaverLanguage):
    
    def __init__(self):
        WeaverLanguage.__init__(self, {
            WeaverLanguage.interactive:    'minghci'
        })
    
    def run_interactive(self, lines, imports, wd):
        def do_line(line):
            command = ['ghc'] + imports + ['-e', line]
            
            ghci = Popen(
                command,
                stdout = PIPE,
                stderr = PIPE,
                cwd = wd
            )
            
            out, err = ghci.communicate()

            return err + out
        
        return [do_line(line) for line in lines]
    
    def highlight_lang(self):
        return 'haskell'

# Singleton
MinimalGHCI = MinimalGHCI()

