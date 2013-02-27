
from rstweaver import WeaverLanguage, WeaverSession
from subprocess import Popen, PIPE, STDOUT
from docutils import nodes
import re
from uuid import uuid4
import operator
from code import compile_command
import ast
import shutil
import json
import sys
from StringIO import StringIO
import os
from tempfile import mkstemp
import traceback

class Python(WeaverLanguage):
    
    def __init__(self, **other_options):
        WeaverLanguage.__init__(self, {
            WeaverLanguage.noninteractive: 'python',
            WeaverLanguage.interactive:    'ipython',
            WeaverLanguage.session:        'py'
        },
        **other_options
        )
    
    def test_compile(self, path, wd):
        proc = Popen(
            ['python', path],
            stdout = PIPE,
            stderr = PIPE,
            cwd = wd
        )
        
        out, err = proc.communicate()
        
        return err
    
    def run(self, path, wd):
        proc = Popen(
            ['python', path],
            stdout = PIPE,
            stderr = PIPE,
            cwd = wd
        )
        
        out, err = proc.communicate()
        
        return err + out
    
    def run_interactive(self, lines, imports, wd):
        return self.chopped_interactive(
            lines,
            lambda id: "'%s'\n" % id,
            lambda id: "'%s'" % id,
            reduce(operator.add, [
                '%%run -i %s\n' % im for im in imports
            ], ''),
            lambda line: line,
            ['ipython', '-quick', '-prompt_in1', '\n', '-prompt_out', '\n'],
            wd
        )
    
    def start_session(self, wd):
        return PythonSession(wd)
    
    def highlight_lang(self):
        return 'python'
    
    def extension(self):
        return '.py'
    
    def interactive_prompt(self):
        return 'py> '

class PythonSession(WeaverSession):
    
    def __init__(self, wd):
        outgoing_r, outgoing_w = os.pipe()
        incoming_r, incoming_w = os.pipe()
        
        self.send = os.fdopen(outgoing_w, 'wb')
        self.recv = os.fdopen(incoming_r, 'rb')
        
        self.proc = Popen(
            ['python', '-c',
                ('from rstweaver.languages.python import PythonServer\n' +
                'PythonServer(%d, %d).run()') % (outgoing_r, incoming_w)
            ],
            cwd = wd
        )
    
    def run(self, input):
        sent = json.dumps({'text': input})
        self.send.write(sent+'\n')
        self.send.flush()
        resp = self.recv.readline()
        try:
            resp = json.loads(resp)
        except:
            print('Failed to parse %s' % resp)
            return []
        
        return [
            (chunk['text'], self.format_output(chunk['output']))
            for chunk in resp
        ]
    
    def format_output(self, output):
        if output == None:
            return None
        
        if type(output) is str or type(output) is unicode:
            return nodes.literal_block(output, output)
        
        if type(output) is dict:
            if output['type'] == 'image':
                return nodes.image(**output['attributes'])
            
        if type(output) is list:
            parent = nodes.inline()
            for out in output:
                parent += self.format_output(out)
            return parent
        
        raise TypeError('%s: %s' % (repr(output), repr(type(output))))
        
class PythonServer:
    
    def __init__(self, recv_fd, send_fd):
        self.stdout_fd = sys.stdin.fileno()
        self.save_stdout = os.dup(self.stdout_fd)
        
        self.recv = os.fdopen(recv_fd, 'r')
        self.send = os.fdopen(send_fd, 'w')
        
        self.globals = {
            'image': self.user_image,
            'draw':  self.user_draw
        }
        self.locals  = None
        self.outputs = [ ]
    
    def run(self):
        while True:
            in_line = self.recv.readline()
            last_text = in_line
            if len(in_line) == 0:
                break
            
            text = self.parse(in_line)
            last_text = text
            outputs = self.process(text)
            out_line = self.format(outputs)
        
            self.send.write(out_line+'\n')
            self.send.flush()
                
    def process(self, full_text):
        lines = re.findall('\n?[^\n]*', full_text)
        
        mod = ast.parse(full_text)
        line_starts = [st.lineno-1 for st in mod.body] + [-1]
        
        def flatten(s):
            p = ''
            for l in s: p += l
            return p
        chunks = [
            (
                flatten(lines[line_starts[k]:line_starts[k+1]]),
                compile(ast.Module([mod.body[k]]), '', 'exec')
            )
            for k in range(len(mod.body))
        ]
        
        return [ self.run_chunk(c) for c in chunks ]
    
    def run_chunk(self, chunk):
        text, code = chunk
        
        # self.outputs will be filled with stuff
        self.outputs = [ ]
        
        sink_fd, _ = mkstemp()
        os.dup2(sink_fd, 1)
        
        # TODO: cleverer outputs
        try:
            sys.stdout.flush()
            eval(code, self.globals, self.locals)
            sys.stdout.flush()
        except Exception as error:
            return text, [traceback.format_exc(error)]
        
        sys.stdout.flush()
        os.lseek(sink_fd, 0, 0)
        sink_in = os.fdopen(sink_fd, 'rb')
        text_out = sink_in.read()
        sink_in.close()
        
        # Restore
        os.dup2(self.save_stdout, self.stdout_fd)
        
        if len(text_out) > 0:
            self.outputs.append(text_out)
        
        if len(self.outputs) == 0:
            return text, None
        else:
            return text, self.outputs
    
    def parse(self, in_line):
        struct = json.loads(in_line)
        return struct['text']
    
    def format(self, outputs):
        return json.dumps([
            {
                'text': text,
                'output': output
            }
            for text, output in outputs
        ])
    
    def user_image(self, filename, unique=False, **attributes):
        if not unique:
            ext = re.sub(r'.*\.', '.', filename)
            new_name = uuid4().hex + ext
            shutil.copyfile(filename, new_name)
        else:
            new_name = filename
        
        self.outputs.append({
            'type': 'image',
            'attributes': { 'uri': os.path.relpath(new_name, '..') }
        })
        
    def user_draw(self, object, **attributes):
        import pygraphviz as pgv
        import matplotlib.pyplot as pp
        name = uuid4().hex + '.png'
        
        if type(object) is pgv.AGraph:
            object.draw(name, prog='dot')
            self.user_image(name, unique=True)
            
        elif object == pp:
            pp.savefig(name)
            self.user_image(name, unique=True)
            
        else:
            raise TypeError('Do not know how to draw %s' % repr(type(object)))

    
