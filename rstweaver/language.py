
class WeaverLanguage(object):
    '''
    Extend this class to create a Weaver language.
    
    Pass to the constructor a dict with some subset of the
    following keys:
        -- WeaverLanguage.noninteractive
        -- WeaverLanguage.interactive
    
    The values of the dict should be the reST directive names
    associated with those modes. So for example for Haskell you could
    do:
        WeaverLanguage.__init__(self, {
            WeaverLanguage.noninteractive: 'haskell',
            WeaverLanguage.interactive:    'ghci'
        })
    
    Look at the methods defined by this class to see what
    you should implement. Some are only required to support one
    mode (noninteractive or interactive).
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
    
    def run_interactive(self, line, imports, wd):
        '''
        This should run one line in an interactive mode, and return
        output/errors.
        
        It may also get passed a list of files to "import" (whatever that means
        for this language) before running the line.
        
        Should the interactive interpreter have "memory"? unfortunately right
        now that's kind of up to you. It would probably be nice, though it's
        hard to implement for some languages. Whatever you want.

        Parameters:
            line    -- One line of source code
            imports -- List of files (relative paths) to "import"
            wd      -- Working directory for interpreter.
        
        Required for:
            Interactive
        '''
        raise NotImplementedError

    def highlight(self, code):
        '''
        This should return an HTML/CSS highlighted version of the code.
        
        Parameters:
            code            -- Code to highlight
        
        Don't encase returned code in a <div>, it might need to be inlined.
        
        Required for:
            All
        '''
        raise NotImplementedError
    
    def html_prefix(self):
        '''
        Pieces of HTML (usually CSS) to include before the rest of
        the document.
        
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
    
    def output_format(self):
        return 'text'
    
    def run_get_block(self, path, wd, blockid):
        raise NotImplementedError
    
    def annotate_block(self, code, blockid):
        return code
    
    def number_lines(self):
        return True

