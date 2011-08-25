
from language import WeaverLanguage

import os
import sys
from tempfile import mkdtemp
from uuid import uuid4
from utils import makepdir
import operator
from docutils.parsers.rst import directives as rst_directives
from directives import NoninteractiveDirective, InteractiveDirective, WriteAllDirective
from structure import FileSetManager
from docutils.parsers.rst import Directive, directives

class WeaverContext(object):
    
    def __init__(self, wd=None, languages=[]):
        languages = [lang(context = self) for lang in languages]
        self.languages = languages
        
        if wd == None:
            wd = mkdtemp()
        
        self.wd = wd
        self.root_dir = wd
        
        makepdir(self.wd)
        makepdir(self.root_dir)
        
        self.fsm = FileSetManager(self)
        self.registered = False
    
    def register_global_directives(self):
        if self.registered:
            return
        self.registered = True
        
        rst_directives.register_directive('write-all',
            self.write_all_directive())
    
    def register_language_directives(self, language):
        directives = self.language_directives(language)
        
        for directive in directives:
            rst_directives.register_directive(directive.name, directive)
        
    def directive_dict(self):
        return dict(
            (dir.name, dir) for dir in self.all_directives()
        )
    
    def all_directives(self):
        directives = [ ]
        for language in self.languages:
            directives += self.language_directives(language)
        
        directives.append(self.write_all_directive())
        
        return directives
        
    def language_directives(self, language):
        directives = [ ]
        
        if WeaverLanguage.noninteractive in language.directives:
            directives.append(self.noninteractive_directive(language))
        
        if WeaverLanguage.interactive in language.directives:
            directives.append(self.interactive_directive(language))
        
        return directives
    
    def noninteractive_directive(self, language):
        context = self
        name = language.directives[WeaverLanguage.noninteractive]

        class Factory(Directive):
            def __init__(self):
                self.optional_arguments = 5
                self.has_content = True
                self.option_spec = {
                    'name':      directives.unchanged,
                    'after':     directives.unchanged,
                    'in':        directives.unchanged,
                    'highlight': directives.unchanged
                }
                self.name = name

            def __call__(self, *a, **b):
                return NoninteractiveDirective(context, name, language, *a, **b)

        return Factory()
    
    def interactive_directive(self, language):
        context = self
        name = language.directives[WeaverLanguage.interactive]

        class Factory(Directive):
            def __init__(self):
                self.optional_arguments = 100
                self.has_content = True
                self.option_spec = {
                }
                self.name = name

            def __call__(self, *a, **b):
                return InteractiveDirective(context, name, language, *a, **b)

        return Factory()
    
    def session_directive(self, language):
        context = self
        name = language.directives[WeaverLanguage.session]
        
        class Factory(Directive):
            def __init__(self):
                self.optional_arguments = 5
                self.has_content = True
                self.option_spec = {
                    'name':      directives.unchanged,
                    'after':     directives.unchanged,
                    'in':        directives.unchanged,
                    'highlight': directives.unchanged
                }
                self.name = name

            def __call__(self, *a, **b):
                return SessionDirective(context, name, language, *a, **b)

        return Factory()
    
    def write_all_directive(self):
        context = self
        name = 'write-all'

        class Factory(Directive):
            def __init__(self):
                self.name = name

            def __call__(self, *a, **b):
                return WriteAllDirective(context, name, *a, **b)

        return Factory()
    
    def run_cache(self, action, producer):
        return self.fsm.run_cache(action, producer)
    
    def is_empty(self, source):
        return self.fsm.is_empty(source)
    
    def feed(self, source, block, redo, after, into):
        return self.fsm.feed(source, block, redo, after, into)
    
    def recall(self, source, name):
        return self.fsm.recall(source, name)
    
    def restart(self, source):
        return self.fsm.restart(source)
    
    def run(self, name, language):
        return self.fsm.run(name, language)
    
    def compile(self, name, language):
        return self.fsm.compile(name, language)
        
    def run_interactive(self, imports, lines, language):
        return self.fsm.run_interactive(imports, lines, language)
    
    def write_all(self):
        self.fsm.write_all()
        
    def total_blocks(self):
        return self.fsm.total_blocks()
    
    def count_lines(self, source):
        return self.fsm.count_lines(source)
    
    def no_cache(self):
        self.fsm.no_cache()

# Singleton (blame docutils!)
def get_weaver_context(wd=None):
    global weaver_context
    
    if weaver_context != None:
        return weaver_context
    
    weaver_context = WeaverContext(wd)
    return weaver_context

weaver_context = None

