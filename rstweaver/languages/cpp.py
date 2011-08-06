
from rstweaver  import WeaverLanguage
from subprocess import Popen, PIPE, STDOUT
import re
from uuid import uuid4
import operator

class CPP(WeaverLanguage):
    
    def __init__(self):
        WeaverLanguage.__init__(self, {
            WeaverLanguage.noninteractive: 'cpp',
            WeaverLanguage.interactive:    'icpp'
        })
    
    def test_compile(self, path, wd):
        proc = Popen(
            ['g++', '-c', '-o', '/dev/null', path],
            stdout = PIPE,
            stderr = PIPE,
            cwd = wd
        )
        
        out, err = proc.communicate()
        
        return err + out
    
    def run(self, path, wd):
        proc = Popen(
            ['g++', '-o', 'main', path],
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
    
    def run_interactive(self, lines, imports, wd):
        includes = [f for f in imports if re.search(r'\.[hH]\w*$', f) != None]
        links    = [f for f in imports if re.search(r'\.[cC]\w*$', f) != None]
        
        ids = [uuid4().hex for j in range(len(lines)+1)]
        
        def print_id(id):
            return 'std::cout << "%s\\n";\n' % id
        pids = map(print_id, ids)
        
        def include(path):
            return '#include "%s"\n' % path
        includes = reduce(operator.add, map(include, ['iostream'] + includes))
        
        input = (
              includes
            + '\n\nint main() {\n'
            + reduce(operator.add, [
                  lines[k].rstrip().lstrip() + ';\n'
                + pids[k+1]
                for k in range(len(lines))
            ], pids[0])
            + '\n}\n'
        )
        
        with open(wd + '/main.cpp', 'w') as hl:
            hl.write(input)
        
        proc = Popen(
            ['g++', '-o', 'main', 'main.cpp'] + links,
            stdout = PIPE,
            stderr = PIPE,
            cwd = wd
        )
        out, err = proc.communicate()
        status = proc.wait()
        
        if status != 0:
            return [out + err] + ([''] * (len(lines)-1))
        
        proc = Popen(
            ['./main'],
            stdout = PIPE,
            stderr = STDOUT,
            cwd = wd
        )
        out, err = proc.communicate()
        
        out_lines = [''] * len(lines)
        [_,rest] = out.split(ids[0])
        for k in range(len(lines)):
            [out_lines[k],rest] = rest.split(ids[k+1])
        
        return [l.rstrip().lstrip() for l in out_lines]
    
    def highlight_lang(self):
        return 'cpp'
    
    def interactive_prompt(self):
        return 'c++> '

CPP = CPP()

