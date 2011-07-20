
from rstweaver import WeaverLanguage
from subprocess import Popen, PIPE
from xml.sax.saxutils import escape

class MinimalHaskell(WeaverLanguage):
    
    def __init__(self):
        WeaverLanguage.__init__(self, {
            WeaverLanguage.noninteractive: 'minhaskell'
        })
    
    def test_compile(self, path, wd):
        ghc = Popen(
            ['ghc', '-c', '-o', '/dev/null', path],
            stdout = PIPE,
            stderr = PIPE,
            cwd = wd
        )
        out, err = ghc.communicate()
        
        return err
    
    def run(self, path, wd):
        runghc = Popen(
            ['runghc', path],
            stdout = PIPE,
            stderr = PIPE,
            cwd = wd
        )
        
        out, err = runghc.communicate()
        
        return err + out
    
    def highlight(self, code):
        return escape(code)

# Singleton
MinimalHaskell = MinimalHaskell()

