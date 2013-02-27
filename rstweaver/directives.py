
from docutils.parsers.rst import Directive, directives
from docutils import nodes
from structure import Block
from uuid import uuid4
import re
from highlight import highlight_as
import os

class WeaverDirective(Directive):
    def __init__(self, context, name, use_cache, *a, **b):
        Directive.__init__(self, *a, **b)
        self.context        = context
        self.directive_name = name
        self.use_cache      = use_cache
    
    def run(self):
        args    = self.arguments
        options = self.options
        content = self.content
        
        if self.use_cache or 'nocache' in options:
            key = (
                self.directive_name,
                tuple(args),
                tuple(options.items()),
                tuple(content)
            )
            
            output = self.context.run_cache(
                key,
                lambda: self.handle(args, options, content)
            )
            return output
        else:
            return self.context.with_no_cache(
                lambda: self.handle(args, options, content)
            )
    
    def handle(self, args, options, content):
        raise NotImplementedError

class ContentDirective:
    def actual_content(self, args, options, maybe_content):
        if 'file' in options:
            path = options['file']
            with open(path) as hl:
                return hl.read().split('\n')
        return maybe_content

class FileManagingDirective:
    def do_recall(self, source, commands, options, content):
        block_name = (self.options['name']
            if 'name' in self.options else None
        )
        text = self.context.recall(source, block_name)
        return [Block.just_text(text)]
    
    def do_mods(self, source, commands, options, content):
        cx = self.context
        
        if 'restart' in commands:
            cx.restart(source)

        block_name = (self.options['name']
            if 'name' in self.options
            else None
        )
        
        redo = 'redo' in commands
        into = options.get('in', None)
        after = options.get('after', None)
        before = options.get('before', None)

        lines = map(unicode, content)
        
        block = self.expand_subparts(lines, block_name)
        
        if not ('noeval' in commands):
            cx.feed(source, block, redo, after, before, into)
            
        return block.subblocks
    
    def expand_subparts(self, lines, block_name):
        leading = ()
        parts   = ()
        
        while 1:
            if len(lines) == 0:
                if len(leading) > 0:
                    back = Block.with_lines(None, leading)
                    parts = parts + (back,)
                break
            
            else:
                head = lines[0]
                rest = lines[1:]
                match = re.match(r'^\s*\<\<\<([^\>]*)\>\>\>\s*$', head)
                
                if match != None:
                    back = Block.with_lines(None, leading)
                    leading = ()
                    
                    takeout = Block.empty(match.groups(1)[0])
                    parts = parts + (back,takeout)
                
                else:
                    head = re.subn(r'\<\<\<\<([^\>]*)\>\>\>\>', r'<<<\1>>>', head)[0]
                    leading = leading + (head,)
                
                lines = rest
        
        return Block.with_parts(block_name, parts)

class BlockDisplayDirective:
    def render_input(self, input_blocks, options, was_lines, header_node=None):
        ''' Renders the result of do_mods.'''
        # I forget what this means.
        if input_blocks == None:
            return None
        
        source_nodes = []
        for sblock in input_blocks:
            if sblock.name == None:
                source_nodes += self.render_input_string(sblock.text(), options)
            else:
                source_nodes += [nodes.inline('',
                    '[... %s ...]' % sblock.name,
                    classes = ['omission']
                ), nodes.inline('\n', '\n')]
                
        if self.language.number_lines():
            source_nodes = add_line_numbers(source_nodes, was_lines+1)
        
        return self.wrap_in_code(source_nodes, header_node)
    
    def render_input_string(self, text, options):
        if 'highlight' in options:
            hlbtext = highlight_as(text, options['highlight'])
        else:
            hlbtext = self.language.highlight(text)
        return hlbtext
    
    def wrap_in_code(self, content_nodes, header_node=None):
        source_node = nodes.literal_block(
            classes=['code', 'code-' + self.directive_name])
        if header_node != None: source_node += header_node
        for n in content_nodes:
            source_node += n
            
        return source_node
    
    def render_output(self, output_obj, options):
        ''' Renders the result of do_run().'''
        # This means there was no output
        if output_obj == None:
            return None
        
        if type(output_obj) is str:
            output = strip_blank_lines(output_obj)
            try:
                output = output.decode('utf-8')
            except:
                output = filter(lambda c: ord(c)<128, output)
            output_node = nodes.literal_block(output, output,
                classes=['run-output', 'run-output-' + self.directive_name]
            )
        else:
            output_node = output_obj
            
        return output_node

class NoninteractiveDirective(WeaverDirective, FileManagingDirective, BlockDisplayDirective, ContentDirective):
    def __init__(self, context, name, language, *a, **b):
        WeaverDirective.__init__(self, context, name, True, *a, **b)
        self.language = language
        
    def handle(self, args, options, maybe_content):
        content = self.actual_content(args, options, maybe_content)
        
        file_like_args    = [arg for arg in args if arg.find('.') != -1]
        command_like_args = [arg for arg in args if arg.find('.') == -1]
        
        def cmd(s):
            return directives.choice(s, [
                'exec', 'done', 'restart', 'noeval', 'redo',
                'join', 'noecho', 'new', 'recall'
            ])
        commands = map(cmd, command_like_args)

        if len(file_like_args) > 0: source_name = file_like_args[0]
        elif 'new' in commands:
            source_name = 'main' + str(unique_block_id()) + self.language.extension()
        else: source_name = 'main' + self.language.extension()
        
        was_empty = self.context.is_empty(source_name)
        was_lines = self.context.count_lines(source_name)
 
        if 'recall' in commands:
            input_display  = self.do_recall(source_name, commands, options, content)
            output_display = None
        else:
            input_display  = self.do_mods(source_name, commands, options, content)
            output_display = self.do_run(source_name, commands, options, content)
            
        if 'join' in commands: header_node = nodes.inline()
        else:
            cont = '(cont)' if not was_empty else ''
            header_text = '     %s %s\n\n' % (source_name, cont)
            header_node = nodes.inline(
                header_text, header_text, classes=['file-header']
            )
        
        if 'noecho' in commands: return [ ]
        else:
            source_node = self.render_input(input_display, options, was_lines,
                header_node=header_node)
            output_node = self.render_output(output_display, options)
        
            result = []
            if source_node != None: result.append(source_node)
            if output_node != None: result.append(output_node)
        
            return result
        
    def do_run(self, source, commands, options, content):
        if 'done' in commands:
            return self.context.compile(source, self.language)
        
        elif 'exec' in commands:
            return self.context.run(source, self.language)
    
class InteractiveDirective(WeaverDirective):
    def __init__(self, context, name, language, *a, **b):
        WeaverDirective.__init__(self, context, name, True,  *a, **b)
        self.language = language
    
    def handle(self, args, options, content):
        cx = self.context

        file_like_args = args
        lines = map(str, content)
        
        output_lines = cx.run_interactive(file_like_args, lines, self.language)
        if len(output_lines) < len(lines):
            output_lines = output_lines + ([''] * (len(lines) - len(output_lines)))
        
        sess_nodes = []
            
        for k in range(len(lines)):
            input_node = nodes.inline(classes = ['interactive-input'])
            input_node += nodes.inline('', self.language.interactive_prompt())
            for n in self.language.highlight(lines[k].rstrip().lstrip()):
                input_node += n
            
            output_line = output_lines[k]
            output_line = filter(
                lambda c: ord(c) < 128, output_line
            )
            output_node = nodes.inline('', output_line,
                classes = ['interactive-output'])
            
            sess_nodes += [input_node, nodes.inline('\n','\n'), output_node]
            if k < len(lines)-1:
                sess_nodes += [nodes.inline('\n\n','\n\n')]
        
        all_node = nodes.literal_block(classes=['interactive-session'])
        for n in sess_nodes:
            all_node += n
            
        return [all_node]

class SessionDirective(WeaverDirective, FileManagingDirective, BlockDisplayDirective):
    def __init__(self, context, name, language, *a, **b):
        WeaverDirective.__init__(self, context, name, False, *a, **b)
        self.language = language
        
    def handle(self, args, options, content):
        file_like_args    = [arg for arg in args if arg.find('.') != -1]
        command_like_args = [arg for arg in args if arg.find('.') == -1]
        
        def cmd(s):
            return directives.choice(s, [
                'restart', 'noeval', 'redo', 'wait', 'noecho'
            ])
        commands = map(cmd, command_like_args)
        source = self.name + '-input' + self.language.extension()
        
        blocks = self.do_mods(source, commands, options, content)
        
        # Docutils nodes to return
        result = [ ]
        
        # 'wait' means they are building up a session but don't want
        # to run it yet.
        if 'wait' not in commands:
            chunks = self.context.run_session(source, self.language)
            building_input = ''
            
            for input, output in chunks:
                building_input += input
                
                if output != None:
                    input_node = self.wrap_in_code(
                        self.render_input_string(building_input.strip(), options))
                    output_node = self.render_output(output, options)
                
                    result += [input_node, output_node]
                    building_input = ''
                    
            if len(building_input) > 0:
                input_node = self.wrap_in_code(
                    self.render_input_string(building_input.strip(), options))
                result += [input_node]
                
            self.context.restart(source)
            
        else:
            input_node = self.render_input(blocks, options, was_lines)
            results.append(input_node, options)
            
        return result
        
class WriteAllDirective(WeaverDirective):
    def __init__(self, context, name, *a, **b):
        WeaverDirective.__init__(self, context, name, False, *a, **b)
    
    def handle(self, args, options, content):
        self.context.write_all()
        return []

def strip_blank_lines(text):
    text = re.sub(r'^\s*\n', '', text)
    text = re.sub(r'\n\s*$', '', text)
    return text

def add_line_numbers(toks, start):
    def ln(n):
        return nodes.inline('', '%3d  ' % n, classes=['lineno'])
    
    def gen():
        yield ln(start)
        line = start + 1
        for j in range(len(toks)):
            node = toks[j]
            
            text = node.rawsource
            parts = text.split('\n')
            
            if len(parts) == 1:
                yield node
            else:
                classes = node.attributes['classes']
                
                for k in range(len(parts)):
                    yield nodes.inline('', parts[k], classes=classes)
                    if k < len(parts)-1:
                        yield nodes.inline('\n', '\n')
                        if k < len(parts)-2 or j < len(toks)-1:
                            yield ln(line)
                        line += 1
        
    return list(gen())

def unique_block_id():
    return uuid4().hex[:4]

