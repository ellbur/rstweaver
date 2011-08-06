
import pygments
from pygments.lexers import get_lexer_by_name
from pygments.formatters.html import _get_ttype_class
from docutils import nodes
from uuid import uuid4
import operator
from subprocess import Popen, PIPE, STDOUT

class WeaverLanguage(object):
    '''
    Extend this class to create a Weaver language.
    
    Pass to the constructor a dict with some subset of the following keys:
        -- WeaverLanguage.noninteractive
        -- WeaverLanguage.interactive
    
    The values of the dict should be the reST directive names associated with
    those modes. So for example for Haskell you could do:
        WeaverLanguage.__init__(self, {
            WeaverLanguage.noninteractive: 'haskell',
            WeaverLanguage.interactive:    'ghci'
        })
    
    Look at the methods defined by this class to see what you should implement.
    Some methods are only required to support one mode (noninteractive or
    interactive).
    '''
    
    noninteractive = 1
    interactive    = 2
    
    def __init__(self, directives):
        self.directives = directives
    
    def test_compile(self, path, wd):
        '''
        This should test compilation of the source file and report any errors.
        It should have no effect on later actions (ie don't leave object files
        around (and especially not .hi files)).

        Parameters:
            path -- (Relative) path to the source file.
            wd   -- Working directory from which to run the compiler.
        
        Returns:
            Errors/warnings as text.
        
        Required for:
            Noninteractive
        '''
        raise NotImplementedError
    
    def run(self, path, wd):
        '''
        This should execute the source file and produce output/errors. Be
        careful not te leave object files (or especially .hi files) sitting
        around.
        
        Parameters:
            path -- (Relative) path to the source file.
            wd   -- Working directory from which to run the compiler.
        
        Returns:
            Output/errors/warnings as text.
        
        Required for:
            Noninteractive
        '''
        raise NotImplementedError
    
    def run_interactive(self, lines, imports, wd):
        '''
        This should run several lines of input in interactive mode, and return
        output as a list of the same length.
        
        It may also get passed a list of files to "import" (whatever that means
        for this language) before running the line.
        
        Should the interactive interpreter have "memory"? unfortunately right
        now that's kind of up to you. It would probably be nice, though it's
        hard to implement for some languages. Whatever you want.
        
        You will probably find self.chopped_interactive() helpful.

        Parameters:
            lines   -- List of strings of source code
            imports -- List of files (relative paths) to "import"
            wd      -- Working directory for interpreter.
        
        returns:
            List of lines of output (plain text).
        
        Required for:
            Interactive
        '''
        raise NotImplementedError
    
    def chopped_interactive(
        self, lines, put_id, get_id,
        preamble, wrap_line, command, wd
    ):
        '''
        Run an interactive session by a hacky uuid-chopping method.
        
        The issue this is trying to solve is that most interactive interpreters
        operate on streams of text, not transactions, so it is tricky to tell
        which line of output corresponds to which line of input. The solution
        is a sesson like the following:
        
        > 'aa2252eaf'
        'aa2252eaf
        > 2 + 2
        4
        > '2214e4fac'
        '2214e4fac'
        
        Where those obnoxious hex strings act like delimiters.
        
        You provide the following information:
            lines  - The lines of input to run
            put_id - A function taking a string and making a "print statement"
              out of it
            get_id - A function taking a string and producing what the output
              of the "print statement" will look like.
            preamble - Any text to feed to the interpreter before the start of
              the session.
            wrap_line - A function taking a line of user-supplied input, and
              producing the text that will be sent to the interpreter.
            command - command to sent to Popen (so command + args as a list)
            wd - Working directory path.
        
        And this will return the corresponding output lines.
        '''
        ids = [uuid4().hex for j in range(len(lines)+1)]
        input = (
              preamble
            + reduce(operator.add, [
                  wrap_line(lines[k].rstrip().lstrip()) + '\n'
                + put_id(ids[k+1])
                for k in range(len(lines))
            ], put_id(ids[0]))
        )
        
        proc = Popen(
            command,
            stdin  = PIPE,
            stdout = PIPE,
            stderr = STDOUT,
            cwd = wd
        )
        
        out, err = proc.communicate(input)
        
        out_lines = [None] * len(lines)
        [_,rest] = out.split(get_id(ids[0]))
        for k in range(len(lines)):
            [out_lines[k], rest] = rest.split(get_id(ids[k+1]))
        
        return [l.rstrip().lstrip() for l in out_lines]
    
    def highlight_lang(self, code):
        '''
        Return the name of the language to highlight in.
        '''
        raise NotImplementedError

    def highlight(self, code):
        '''
        This should return a *list* of docutils nodes representing the
        highlighted tokens.
        
        Usually the easient way to do this is to implement
        self.highlight_lang(), and let the default work.
        
        Parameters:
            Code - the code to highlight.
        
        Required for:
            All
        '''
        tokens = pygments.lex(code, get_lexer_by_name(
            self.highlight_lang()
        ))
        
        def make_nodes():
            for ttype, text in tokens:
                yield nodes.inline(text, text, classes=[
                    _get_ttype_class(ttype)
                ])
        
        return list(make_nodes())
    
    def css(self):
        '''
        CSS related to this language.
        
        This will be included after all default CSS, so you should be
        able to override all styles.
        
        If you do not override this method it will return an empty string.
        '''
        return ''
    
    def interactive_prompt(self):
        '''
        Prompt string for interactive sessions.
        
        Defaults to '> '.
        
        Returns:
            Prompt string for interactive sessions.
        '''
        return '> '
    
    def extension(self):
        '''
        Typical file name extension.
        '''
        return ''
    
    def number_lines(self):
        '''
        Return true if lines of source should be numbered.
        Defaults to true.
        '''
        return True

