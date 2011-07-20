
from docutils.parsers.rst import Directive, directives
from docutils import nodes
from xml.sax.saxutils import escape
import re

class NoninteractiveDirective(Directive):
    
    def __init__(self, context, *stuff, **more_stuff):
        Directive.__init__(self, *stuff, **more_stuff)
        self.context = context
        
    def run(self):
        cx = self.context
 
        args = self.arguments
        file_like_args = [
            arg for arg in args
            if arg.find('.') != -1
        ]
        command_like_args =[
            arg for arg in args
            if arg.find('.') == -1
        ]
        
        if len(file_like_args) > 0:
            source_name = file_like_args[0]
        else:
            source_name = 'main'
 
        def cmd(s):
            return directives.choice(s, [
                'hold', 'exec', 'done',
                'restart', 'noeval', 'redo',
                'join', 'noecho'
            ])
        
        commands = map(cmd, command_like_args)

        block_name = (self.options['name']
            if 'name' in self.options
            else None
        )
        after_name = (self.options['after']
            if 'after' in self.options
            else None
        )

        if 'restart' in commands:
            cx.file(source_name).restart()

        if 'join' in commands:
            header_html = ''
        else:
            header_html = '''
                <p class="file-header">-- {0} {1} --</p>
                '''.format(
                    escape(source_name),
                    '(cont)' if not cx.file(source_name).empty else ''
                )
        node_header = nodes.raw('', header_html, format='html')
        
        text = u'\n'.join(self.content)
        
        source_html = cx.language.highlight(
            text,
            numbering = True,
            numbering_start = cx.file(source_name).start_line(
                block_name, after_name, 'redo' in commands
            )
        )
        source_html = '<div class="code">{0}</div>'.format(source_html)

        node_source = nodes.raw('', source_html, format='html')
        
        lines = map(str, self.content)
        lines += ['']
        
        if 'redo' in commands:
            cx.file(source_name).redo(lines, block_name)
        elif not ('noeval' in commands):
            cx.file(source_name).feed(lines, block_name, after_name)
        
        result = [ ]

        if 'done' in commands:
            output = strip_blank_lines(cx.file(source_name).compile())
            if len(re.sub('\\s', '', output)) > 0:
                output_html = ('<div class="run-output"><p>{0}</p></div>'
                    .format(escape(output)))
            else:
                output_html = ''
            node_output = nodes.raw('', output_html, format='html')
            result = [node_header, node_source, node_output]

        elif 'exec' in commands:
            output = strip_blank_lines(cx.file(source_name).run())
            output_html = ('<div class="run-output"><p>{0}</p></div>'
                .format(escape(output)))
            node_output = nodes.raw('', output_html, format='html')
            result = [node_header, node_source, node_output]

        else:
            result = [node_header, node_source]
        
        if 'noecho' in commands:
            return [ ]
        else:
            return result

class InteractiveDirective(Directive):

    def __init__(self, context, *stuff, **more_stuff):
        Directive.__init__(self, *stuff, **more_stuff)
        self.context = context
    
    def run(self):
        cx = self.context

        file_like_args = self.arguments
        
        lines = map(str, self.content)
        
        all_html = ''
        
        for line in lines:
            input_html = cx.language.highlight(line, numbering=False)
            output_text = cx.run_interactive(file_like_args, line)
            
            input_html = '<div class="interactive-input">ghci&gt; {0}</div>'.format(
                input_html
            )
            output_html = '<div class="interactive-output">{0}</div>'.format(
                escape(output_text)
            )
            
            all_html += input_html
            all_html += output_html
        
        all_html = '<div class="interactive-session">{0}</div>'.format(
            all_html
        )
        
        return [nodes.raw('', all_html, format='html')]

def strip_blank_lines(text):
    text = re.sub(r'^\s*\n', '', text)
    text = re.sub(r'\n\s*$', '', text)
    return text

