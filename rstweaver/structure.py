
import operator
import db
from db import ActionCache, Action
from treewatcher import run_watch_files
from collections import namedtuple
import os

class FileSetManager(object):
    
    def __init__(self, context):
        self.context = context
        
        self.db = db.make_db(
            context.root_dir + '/cache'
        )
        
        if 'actions' not in self.db:
            self.db['actions'] = ActionCache()
            
        self.actions = self.db['actions']
        self.file_set = FileSet()
        self.watches = [ ]
    
    def run_cache(self, key, producer):
        for action in self.actions[key]:
            if self.file_set.all_up_to_date(action.inputs):
                self.file_set.apply_outputs(action.outputs)
                print('reusing')
                return action.output
        
        print('generating')
        
        watch = self.add_watch()
        output = producer()
        self.end_watch(watch)
        
        for path in watch.outputs_external:
            full_path = self.context.wd + '/' + path
            try:
                if os.path.exists(full_path):
                    with open(full_path, 'rb') as hl:
                        content = hl.read()
                else:
                    content = None
            except IOError as e:
                print('Warning, while running %s got %s' % (str(key), str(e)))
                content = None
            
            file = self.file_set.file(path)
            old_content = file.text()
            
            if content != None and (old_content != content):
                self.file_set.files[path] = File.binary(path, content)
        
        outputs = [self.file_set.file(file) for file in
            (watch.outputs_internal.union(watch.outputs_external))]
        
        self.actions[key] = Action(watch.inputs, outputs, output)
        
        return output
    
    def add_watch(self):
        watch = Watch(self.file_set.files)
        self.watches.append(watch)
        return watch
    
    def end_watch(self, watch):
        self.watches.remove(watch)
        
    def watch_input(self, name):
        for watch in self.watches:
            watch.add_input(name)
    
    def watch_output_internal(self, name):
        for watch in self.watches:
            watch.add_output_internal(name)
    
    def watch_output_external(self, name):
        for watch in self.watches:
            watch.add_output_external(name)
    
    def write_all(self):
        self.file_set.write_all(self.context.wd)
        
    def total_blocks(self):
        return sum(len(f.blocks)
            for f in self.file_set.files.values()
        )
    
    def is_empty(self, source):
        self.watch_input(source)
        file = self.file_set.file(source)
        return file.is_empty()
    
    def count_lines(self, source):
        self.watch_input(source)
        file = self.file_set.file(source)
        return file.count_lines()
    
    def restart(self, source):
        self.watch_output_internal(source)
        self.file_set.files[source] = File.empty(source)
    
    def feed(self, source, block, redo, after, into):
        self.watch_input(source)
        self.watch_output_internal(source)
        
        file = self.file_set.file(source)
        
        self.file_set.files[source] = file.feed(block, redo, after, into)
        
    def run_interactive(self, imports, lines, language):
        return self.do_watched(
            lambda: language.run_interactive(lines, imports, self.context.wd)
        )
    
    def recall(self, source_name, block_name):
        self.watch_input(source_name)
        return self.file_set.file(source_name).recall(block_name)
    
    def run(self, name, language):
        return self.do_watched(
            lambda: language.run(name, self.context.wd)
        )
    
    def compile(self, name, language):
        return self.do_watched(
            lambda: language.test_compile(name, self.context.wd)
        )
    
    def do_watched(self, proc):
        self.write_all()
        
        wd = self.context.wd
        output, mods = run_watch_files(proc, wd)
        
        inputs = mods.accessed
        outputs = mods.modified.union(mods.created)
        
        inputs  = [os.path.relpath(path, wd) for path in inputs]
        outputs = [os.path.relpath(path, wd) for path in outputs]
        
        for file in inputs:
            self.watch_input(file)
        for file in outputs:
            self.watch_output_external(file)
        
        return output

class Watch(object):
    
    def __init__(self, start_files):
        self.start_files = dict(start_files)
        
        self.inputs = set()
        self.outputs_internal = set()
        self.outputs_external = set()
    
    def add_input(self, name):
        if name in self.start_files:
            file = self.start_files[name]
        else:
            file = File.empty(name)
        self.inputs.add(file)
    
    def add_output_internal(self, name):
        self.outputs_internal.add(name)
    
    def add_output_external(self, name):
        self.outputs_external.add(name)
    
class FileSet(object):
    
    def __init__(self):
        self.files   = { }
    
    def file(self, name):
        if name not in self.files:
            self.files[name] = File.empty(name)
            
        return self.files[name]
    
    def write_all(self, wd):
        for name, file in self.files.items():
            file.write(wd)
    
    def all_up_to_date(self, inputs):
        for input in inputs:
            if self.file(input.name) != input:
                return False
        return True
    
    def apply_outputs(self, outputs):
        for output in outputs:
            self.files[output.name] = output
    
_File = namedtuple('File', ['name', 'block'])

class File(_File):
    
    @staticmethod
    def binary(name, content):
        return File(name, Block.binary(content))
    
    @staticmethod
    def empty(name):
        return File(name, Block.empty())
    
    def is_empty(self):
        return self.block.is_empty()
    
    def count_lines(self):
        return self.block.count_lines()
    
    def feed(self, block, redo, after, into):
        old_block = self.block
        if into != None:
            new_block = old_block.into(block, into)
            if new_block == None: raise NameNotFound(into)
        elif after != None:
            new_block = old_block.after(block, after)
            if new_block == None:
                raise NameNotFound(after)
        elif redo:
            new_block = old_block.redo(block, block.name)
            if new_block == None: raise NameNotFound(block.name)
        else:
            new_block = old_block.append(block)
        
        return self._replace(block = new_block)
    
    def recall(self, name):
        res = self.block.recall(name)
        if res == None:
            raise NameNotFound(name)
        return res
    
    def restart(self):
        return File(self.name, Block.empty(None))
    
    def text(self):
        return self.block.text()
    
    def write(self, wd):
        with open(wd + '/' + self.name, 'w') as hl:
            hl.write(self.text())
    
    def __str__(self):
        return '(%s: %s)' % (self.name, self.text())
    
    def __repr__(self):
        return self.__str__()
    
_Block = namedtuple('Block', ['name', 'lines', 'subblocks', 'blob'])

class Block(_Block):
    
    @staticmethod
    def empty(name = None):
        return Block(name, (), (), None)
    
    @staticmethod
    def binary(content):
        return Block(None, (), (), content)
    
    @staticmethod
    def just_text(text):
        return Block(None, tuple(text.split('\n')), (), None)
    
    @staticmethod
    def with_lines(name, lines):
        return Block(name, lines, (), None)
    
    @staticmethod
    def with_parts(name, parts):
        return Block(name, (), parts, None)
    
    def is_empty(self):
        if len(self.lines) > 0: return False
        if len(self.subblocks) > 0: return False
        if self.blob != None: return False
        return True
    
    def count_lines(self):
        return len(self.lines) + sum(
            block.count_lines() for block in self.subblocks
        )
    
    def all_lines(self):
        return self.lines + reduce(operator.add,
            (sblock.all_lines() for sblock in self.subblocks), ())
    
    def text(self):
        if self.blob != None:
            return self.blob
        else:
            return '\n'.join(self.all_lines()) + '\n'
    
    def reverse_searched(handler):
        def decorated(self, *a, **b):
            look_first = reversed(self.subblocks)
            for block in look_first:
                res = decorated(block, *a, **b)
                if res != None: return res
            
            res = handler(self, *a, **b)
            if res != None:
                return res
            
            return None
        
        return decorated
    
    def reverse_replaced(handler):
        def decorated(self, *a, **b):
            sblocks = list(reversed(self.subblocks))
            for i in range(len(sblocks)):
                sblock = sblocks[i]
                res = decorated(sblock, *a, **b)
                
                if res != None:
                    sblocks[i] = res
                    return self._replace(subblocks=tuple(reversed(sblocks)))
            else:
                return handler(self, *a, **b)
        
        return decorated
    
    def append(self, block):
        sblocks = self.subblocks
        sblocks = sblocks + (block,)
        return self._replace(subblocks = sblocks)
    
    @reverse_replaced
    def redo(self, block, name):
        if self.name == name:
            return block
        return None
    
    @reverse_replaced
    def after(self, block, after):
        if after == 'start':
            sblocks = self.subblocks
            sblocks = (block,) + sblocks
            return self._replace(subblocks = sblocks)
        else:
            sblocks = list(reversed(self.subblocks))
            for i in range(len(sblocks)):
                sblock = sblocks[i]
                if sblock.name == after:
                    sblocks.insert(i, block)
                    sblocks = tuple(reversed(sblocks))
                    return self._replace(subblocks=sblocks)
            else:
                return None
    
    @reverse_replaced
    def into(self, block, into):
        if self.name == into:
            sblocks = self.subblocks
            sblocks = sblocks + (block,)
            return self._replace(subblocks = sblocks)
        return None
    
    @reverse_searched
    def recall(self, name):
        if self.name == name:
            return self.text()
        return None

class NameNotFound(Exception):
    
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.__str__()

def not_none(name, obj):
    if obj == None:
        raise NameNotFound(name)
    return obj

