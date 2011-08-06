
from language import WeaverLanguage

import os
import sys
from tempfile import mkdtemp
from uuid import uuid4
from utils import makepdir
import db

from directives import *
from docutils.parsers.rst import Directive, directives

class WeaverContext(object):
    
    def __init__(self, language):
        self.language = language
        self.files = { }
        
        self.root_dir    = os.path.expanduser('~/.cache/rstweaver')
        self.wd          = mkdtemp()
        
        makepdir(self.root_dir)
        makepdir(self.wd)
        
        self.fsm = FileSetManager(self)
    
    def directives(self):
        directives = []
        
        if WeaverLanguage.noninteractive in self.language.directives:
            dir = self.noninteractive_directive()
            directives.append(dir)
        
        if WeaverLanguage.interactive in self.language.directives:
            dir = self.interactive_directive()
            directives.append(dir)
        
        return directives
    
    def noninteractive_directive(self):
        context = self
        name = self.language.directives[WeaverLanguage.noninteractive]

        class Factory(Directive):
            def __init__(self):
                self.optional_arguments = 5
                self.has_content = True
                self.option_spec = {
                    'name':  directives.unchanged,
                    'after': directives.unchanged
                }
                self.name = name

            def __call__(self, *a, **b):
                return NoninteractiveDirective(context, name, *a, **b)

        return Factory()
    
    def interactive_directive(self):
        context = self
        name = self.language.directives[WeaverLanguage.interactive]

        class Factory(Directive):
            def __init__(self):
                self.optional_arguments = 100
                self.has_content = True
                self.option_spec = {
                }
                self.name = name

            def __call__(self, *a, **b):
                return InteractiveDirective(context, name, *a, **b)

        return Factory()
    
    def run_cache(self, action, producer):
        return self.fsm.run_cache(action, producer)
    
    def run_interactive(self, imports, lines):
        self.write_all()
        return self.language.run_interactive(lines, imports, self.wd)
    
    def file(self, name):
        return self.fsm.file_set.file(name)
    
    def write_all(self):
        self.fsm.write_all()

class FileSetManager(object):
    
    def __init__(self, context):
        self.context = context
        
        self.db = db.open_db()
        
        if 'actions' not in self.db:
            self.db['actions'] = { }
            
        self.actions         = self.db['actions']
        self.file_set        = FileSet(context)
        self.snap            = self.file_set.freeze()
        self.set_up_to_date  = True
    
    def run_cache(self, action, producer):
        key = (action, self.snap)
        
        if key in self.actions:
            output, next_snap = self.actions[key]
            self.snap = next_snap
            self.set_up_to_date = False
            return output
        else:
            if not self.set_up_to_date:
                self.file_set = self.snap.restore(self.context)
                
            output = producer()
            
            self.snap = self.file_set.freeze()
            self.set_up_to_date = True
            self.actions[key] = (output, self.snap)
            
            return output
    
    def write_all(self):
        self.file_set.write_all()
        
class FileSet(object):
    
    def __init__(self, context):
        self.context = context
        self.files   = { }
    
    def freeze(self):
        return FileSetSnapshot(self)
    
    def file(self, name):
        if name not in self.files:
            self.files[name] = File(self.context, name)
            
        return self.files[name]
    
    def write_all(self):
        for name, file in self.files.items():
            file.write_if_changed()

class FileSetSnapshot(object):
    
    def __init__(self, set):
        self.files = tuple(sorted([f.freeze() for n,f in set.files.items()]))
    
    def __hash__(self):
        return hash(self.files)
    
    def __cmp__(self, other):
        return cmp(self.files, other.files)
    
    def restore(self, context):
        set = FileSet(context)
        for f in self.files:
            set[f.name] = f.restore(context)
        
        return set

class File(object):

    def __init__(self, context, name):
        self.context = context
        self.name    = name
        
        self.empty   = True
        self.blocks  = [ ]
        self.up_to_date = False
    
    def feed(self, lines, name=None, after=None):
        self.up_to_date = False
        
        new_block = Block(lines, name)

        if after == 'start':
            self.blocks.insert(0, new_block)
        elif after != None:
            for k in range(len(self.blocks)):
                block = self.blocks[k]
                if block.name == after:
                    self.blocks.insert(k+1, new_block)
                    break
            else:
                raise NameNotFound(after)
        else:
            self.blocks.append(new_block)

        self.empty = False
    
    def redo(self, lines, name):
        self.up_to_date = False
        
        for block in self.blocks:
            if block.name == name:
                block.lines   = lines
                break
        else:
            raise NameNotFound(name)
    
    def restart(self):
        self.up_to_date = False
        
        self.empty = True
        self.blocks = [ ]
    
    def write(self):
        text = self.text()

        with open(self.path(), 'w') as fh:
            fh.write(text)
        
        self.up_to_date = True
    
    def write_if_changed(self):
        if not self.up_to_date:
            self.write()
    
    def text(self):
        lines = [ ]
        for block in self.blocks:
            lines += block.output_lines()
        
        return '\n'.join(lines)
    
    def count_lines(self):
        return sum([
            len(block.lines) for block in self.blocks
        ])
    
    def start_line(self, block_name, after_name, redo):
        lines = 1

        if redo:
            for block in self.blocks:
                if block.name == block_name:
                    return lines
                lines += len(block.lines)
            else:
                raise NameNotFound(block_name)
        
        elif after_name == 'start':
            return 1
        
        elif after_name != None:
            for block in self.blocks:
                lines += len(block.lines)
                
                if block.name == after_name:
                    return lines
            else:
                raise NameNotFound(after_name)
        
        else:
            return self.count_lines() + 1
    
    def compile(self):
        self.context.write_all()
        
        return self.context.language.test_compile(
            self.name,
            self.context.wd
        )
    
    def run(self):
        self.context.write_all()
        
        return self.context.language.run(
            self.name,
            self.context.wd
        )
    
    def path(self):
        return self.context.wd + '/' + self.name
    
    def freeze(self):
        return FileSnapshot(self)

class FileSnapshot(object):
    
    def __init__(self, file):
        self.tuple = (
            file.name,
            tuple(b.freeze() for b in file.blocks)
        )
        self.name = file.name
    
    def __hash__(self):
        return hash(self.tuple)
    
    def __cmp__(self, other):
        return cmp(self.tuple, other.tuple)
    
    def restore(self, context):
        file = File(context, self.name)
        file.blocks = [b.restore() for b in self.tuple[1]]
        
        return file

class Block(object):
    
    def __init__(self, lines, name):
        self.lines   = lines
        self.name    = name
        
    def output_lines(self):
        return self.lines
    
    def freeze(self):
        return BlockSnapshot(self)

class BlockSnapshot(object):
    
    def __init__(self, block):
        self.tuple = (
            tuple(block.lines),
            block.name
        )
    
    def __hash__(self):
        return hash(self.tuple)
    
    def __cmp__(self, other):
        return cmp(self.tuple, other.tuple)
    
    def restore(self):
        return Block(list(self.tuple[0]), self.tuple[1])

class NameNotFound(Exception):
    
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.__str__()


