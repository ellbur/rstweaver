
from rstweaver import WeaverLanguage
from subprocess import Popen, PIPE, STDOUT
import operator

class Haskell(WeaverLanguage):
    
    def __init__(self, **other_options):
        WeaverLanguage.__init__(self, {
            WeaverLanguage.noninteractive: 'haskell',
            WeaverLanguage.interactive:    'ghci'
        },
        **other_options
        )
    
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
    
    def run_interactive(self, lines, imports, wd):
        return self.chopped_interactive(
            lines,
            lambda id: 'putStrLn "%s"\n' % id,
            lambda id: id,
              ':set prompt ""\n'
            + reduce(operator.add, [
                ':load %s\n' % im for im in imports
            ], ''),
            lambda line: line,
            ['ghci', '-ignore-dot-ghci'],
            wd
        )
    
    def highlight_lang(self):
        return 'haskell'
    
    def interactive_prompt(self):
        return 'ghci> '

