
from docutils.parsers.rst import Directive, directives
from docutils import nodes
import re

class WeaverDirective(Directive):
    
    def __init__(self, context, name, *a, **b):
        Directive.__init__(self, *a, **b)
        self.context        = context
        self.directive_name = name
    
    def run(self):
        args    = self.arguments
        options = self.options
        content = self.content
        
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
    
    def handle(self, args, options, content):
        raise NotImplementedError

class NoninteractiveDirective(WeaverDirective):
    
    def __init__(self, context, name, *a, **b):
        WeaverDirective.__init__(self, context, name, *a, **b)
        
    def handle(self, args, options, content):
        cx = self.context
 
        file_like_args = [
            arg for arg in args
            if arg.find('.') != -1
        ]
        command_like_args =[
            arg for arg in args
            if arg.find('.') == -1
        ]
        
        def cmd(s):
            return directives.choice(s, [
                'exec', 'done',
                'restart', 'noeval', 'redo',
                'join', 'noecho', 'new'
            ])
        
        commands = map(cmd, command_like_args)

        if len(file_like_args) > 0:
            source_name = file_like_args[0]
        elif 'new' in commands:
            source_name = 'main' + str(unique_block_id(cx)) + cx.language.extension()
        else:
            source_name = 'main' + cx.language.extension()
 
        block_name = (self.options['name']
            if 'name' in self.options
            else None
        )
        after_name = (options['after']
            if 'after' in self.options
            else None
        )

        if 'restart' in commands:
            cx.file(source_name).restart()

        if 'join' in commands:
            header_node = nodes.inline()
        else:
            cont = '(cont)' if not cx.file(source_name).empty else ''
            header_text = '     %s %s\n\n' % (source_name, cont)
            header_node = nodes.inline(
                header_text, header_text, classes=['file-header']
            )
        
        text = u'\n'.join(content)
        
        source_nodes = cx.language.highlight(text)
        if cx.language.number_lines():
            source_nodes = add_line_numbers(source_nodes,
                cx.file(source_name).start_line(
                        block_name, after_name, 'redo' in commands
                )
            )
        source_node = nodes.literal_block(
            classes=['code', 'code-' + self.directive_name])
        source_node += header_node
        for n in source_nodes:
            source_node += n

        lines = map(str, self.content)
        lines += ['']
        
        if 'redo' in commands:
            cx.file(source_name).redo(lines, block_name)
        elif not ('noeval' in commands):
            cx.file(source_name).feed(lines, block_name, after_name)
        
        result = [ ]

        if 'done' in commands:
            output = strip_blank_lines(cx.file(source_name).compile())
            output = filter(
                lambda c: ord(c) < 128, output
            )
            output_node = nodes.literal_block(output, output,
                classes=['run-output', 'run-output-' + self.directive_name]
            )
            
            result = [source_node, output_node]

        elif 'exec' in commands:
            output = cx.file(source_name).run()
 
            if isinstance(output, str):
                output = strip_blank_lines(output)
                output = filter(
                    lambda c: ord(c) < 128, output
                )
                output_node = nodes.literal_block(output, output,
                    classes=['run-output', 'run-output-' + self.directive_name]
                )
            else:
                output_node = output
            
            result = [source_node, output_node]

        else:
            result = [source_node]
        
        if 'noecho' in commands:
            return [ ]
        else:
            return result

class InteractiveDirective(WeaverDirective):

    def __init__(self, context, name, *a, **b):
        WeaverDirective.__init__(self, context, name, *a, **b)
    
    def handle(self, args, options, content):
        cx = self.context

        file_like_args = args
        lines = map(str, content)
        
        output_lines = cx.run_interactive(file_like_args, lines)
        if len(output_lines) < len(lines):
            output_lines = output_lines + ([''] * (len(lines) - len(output_lines)))
        
        sess_nodes = []
            
        for k in range(len(lines)):
            input_node = nodes.inline(classes = ['interactive-input'])
            input_node += nodes.inline('', cx.language.interactive_prompt())
            for n in cx.language.highlight(lines[k].rstrip().lstrip()):
                input_node += n
            
            output_line = output_lines[k]
            output_line = filter(
                lambda c: ord(c) < 128, output_line
            )
            output_node = nodes.inline('', output_line,
                classes = ['interactive-output'])
            
            sess_nodes += [input_node, output_node]
            if k < len(lines)-1:
                sess_nodes += [nodes.inline('\n\n','\n\n')]
        
        all_node = nodes.literal_block(classes=['interactive-session'])
        for n in sess_nodes:
            all_node += n
            
        return [all_node]

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
        for node in toks:
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
                        yield ln(line)
                        line += 1
        
    return list(gen())

def unique_block_id(cx):
    return cx.total_blocks() + 1

