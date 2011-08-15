
from rstweaver  import WeaverLanguage
from subprocess import Popen, PIPE, STDOUT
import re
import operator

class Bash(WeaverLanguage):
    
    def __init__(self, **other_options):
        WeaverLanguage.__init__(self, {
            WeaverLanguage.noninteractive: 'bash',
            WeaverLanguage.interactive:    'ibash'
        },
        **other_options
        )
    
    def run(self, path, wd):
        proc = Popen(
            ['bash', path],
            stdout = PIPE,
            stderr = PIPE,
            cwd = wd
        )
        
        out, err = proc.communicate()
        
        return err + out
    
    def run_interactive(self, lines, imports, wd):
        return self.chopped_interactive(
            lines,
            lambda id: 'echo %s\n' % id,
            lambda id: '%s' % id,
            reduce(operator.add, [
                '. %s\n' % im for im in imports
            ], ''),
            lambda line: line,
            ['bash'],
            wd
        )
    
    def highlight_lang(self):
        return 'bash'
    
    def extension(self):
        return '.sh'
    
    def interactive_prompt(self):
        return '$ '

