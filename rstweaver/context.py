
from language import WeaverLanguage

import os
import sys
from tempfile import mkdtemp

from directives import *
from docutils.parsers.rst import Directive, directives

class WeaverContext(object):
    
    def __init__(self, language):
        self.language = language
        self.files = { }
        self.wd = mkdtemp()
    
    def directives(self):
        directives = []
        
        if WeaverLanguage.noninteractive in self.language.directives:
            dir = self.noninteractive_directive()
            dir.name = self.language.directives[WeaverLanguage.noninteractive]
            directives.append(dir)
        
        if WeaverLanguage.interactive in self.language.directives:
            dir = self.interactive_directive()
            dir.name = self.language.directives[WeaverLanguage.interactive]
            directives.append(dir)
        
        return directives
    
    def noninteractive_directive(self):
        context = self

        class Factory(Directive):
            def __init__(self):
                self.optional_arguments = 5
                self.has_content = True
                self.option_spec = {
                    'name':  directives.unchanged,
                    'after': directives.unchanged
                }

            def __call__(self, *a, **b):
                return NoninteractiveDirective(context, *a, **b)

        return Factory()
    
    def interactive_directive(self):
        context = self

        class Factory(Directive):
            def __init__(self):
                self.optional_arguments = 1
                self.has_content = True
                self.option_spec = {
                }

            def __call__(self, *a, **b):
                return InteractiveDirective(context, *a, **b)

        return Factory()
    
    def file(self, name):
        if not(name in self.files):
            self.files[name] = WeaverFile(self, name)
        
        return self.files[name]
    
    def run_interactive(self, names, line):
        for name in names:
            self.file(name).write()
        
        return self.language.run_interactive(line, names, self.wd)
        
class WeaverFile:

    def __init__(self, context, name):
        self.context = context
        self.name    = name
        
        self.empty   = True
        self.version = 1
        self.blocks  = [ ]
        
    def feed(self, lines, name=None, after=None):
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
        for block in self.blocks:
            if block.name == name:
                block.lines = lines
                break
        else:
            raise NameNotFound(name)
    
    def restart(self):
        self.empty = True
        self.blocks = [ ]
    
    def write(self):
        text = self.text()

        with open(self.path(), 'w') as fh:
            fh.write(text)

        with open(self.version_path(), 'w') as fh:
            fh.write(text)
        
        self.version += 1
    
    def text(self):
        lines = [ ]
        for block in self.blocks:
            lines += block.lines
        
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
        self.write()
        
        return self.context.language.test_compile(
            self.name,
            self.context.wd
        )
    
    def run(self):
        self.write()
        
        return self.context.language.run(
            self.name,
            self.context.wd
        )
    
    def path(self):
        return self.context.wd + '/' + self.name
    
    def version_path(self):
        d = self.name.rfind('.')
        base = self.name[:d]
        ext = self.name[d:]

        return (
            self.context.wd + '/' +
            base + '-' + str(self.version)
            + ext
        )

class Block:
    
    def __init__(self, lines, name):
        self.lines = lines
        self.name  = name

class NameNotFound(Exception):
    
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.__str__()


