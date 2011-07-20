
from rstweaver import WeaverLanguage
from subprocess import Popen, PIPE

class Haskell(WeaverLanguage):
    
    def __init__(self):
        WeaverLanguage.__init__(self, {
            WeaverLanguage.noninteractive: 'haskell',
            WeaverLanguage.interactive:    'ghci'
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
        proc = Popen([
                'hscolour',
                '-css',
                '-partial',
                '-nopre'
            ],
            stdin  = PIPE,
            stdout = PIPE
        )
        out, err = proc.communicate(code)
        
        return out
    
    def html_prefix(self):
        return haskell_css
    
    def interactive_prompt(self):
        return 'ghci> '

# Singleton
Haskell = Haskell()

haskell_css = '''
<style type="text/css">
.hs-keyglyph {
    color: #911;
}

.hs-layout {
    color: #911;
}

.hs-comment {
    color: #ccc;
    font-style: italic;
}

.hs-comment a {
    color: #ccc;
    font-style: italic;
}

.hs-str {
    color: teal;
    font-style: italic;
}

.hs-chr {
    color: teal;
}

.hs-keyword {
    color: #000;
    font-weight: bold;
}

.hs-conid {
    color: #039;
}

.hs-varid {
    color: #000;
}

.hs-conop {
    color: #900;
}

.hs-varop {
    color: #900;
}

.hs-num {
    color: #0aa;
}

.hs-cpp {
    color: #900;
}

.hs-sel {
    color: #900;
}

.hs-definition {
    color: teal;
}

.hs-lineno {
    color: #aaa;
}
</style>
'''


