
Adding languages
================

If you just want to write a quick bit of Ruby, you're best bet is
:ref:`arbfiles`.

Defining languages
~~~~~~~~~~~~~~~~~~

To add a language you will want to extend ``rstweaver.WeaverLanguage``, and
override some methods.

``WeaverLanguage`` has many methods, but there are only a few that you have do
deal with to get something working.

Non-interactive directives
--------------------------

"Non-interactive" is what the ``haskell`` directive is in the examples above:
whole blocks of code are added to a file, then the file is executed in one go.

Here's a terribly terribly minimal implementation for Haskell:

::

    from rstweaver import WeaverLanguage
    from subprocess import Popen, PIPE

    class MinimalHaskell(WeaverLanguage):
        
        def __init__(self, **other_options):
            WeaverLanguage.__init__(self, {
                WeaverLanguage.noninteractive: 'minhaskell'
            },
            **other_options
            )
        
        def test_compile(self, path, wd):
            ghc = Popen(
                ['ghc', '-c', '-o', '/dev/null', path],
                stdout = PIPE,
                stderr = PIPE,
                cwd = wd
            )
            out, err = ghc.communicate()
            
            return err
        
        def run(self, path, wd):
            runghc = Popen(
                ['runghc', path],
                stdout = PIPE,
                stderr = PIPE,
                cwd = wd
            )
            
            out, err = runghc.communicate()
            
            return err + out
        
        def highlight_lang(self):
            return 'haskell'

Which could be used like

.. weaver:: new exec join

    .. minhaskell:: new exec
    
        main = do
            putStrLn "Yo"
            

The important parts are:

1. Telling ``WeaverLanguage`` you want a non-interactive directive,
   by adding an entry to the dictionary passed to __init__.
2. Implementing ``test_compile``, ``run``, and ``highlight_lang``.

Interactive directives
----------------------

Here's a similarly minimal implementation for interactive Haskell:

::

    from rstweaver import WeaverLanguage
    from subprocess import Popen, PIPE

    class MinimalGHCI(WeaverLanguage):
        
        def __init__(self, **other_options):
            WeaverLanguage.__init__(self, {
                WeaverLanguage.interactive:    'minghci'
            },
            **other_options
            )
        
        def run_interactive(self, lines, imports, wd):
            def do_line(line):
                command = ['ghc'] + imports + ['-e', line]
                
                ghci = Popen(
                    command,
                    stdout = PIPE,
                    stderr = PIPE,
                    cwd = wd
                )
                
                out, err = ghci.communicate()

                return err + out
            
            return [do_line(line) for line in lines]
        
        def highlight_lang(self):
            return 'haskell'

Which can be used like

.. weaver:: new exec join

    .. minghci::
        
        :t (:)

The steps are:

1. Telling WeaverLanguage to register an interactive directive.
2. Defining ``run_interactive`` and ``highlight_lang``
   
You might notice that this implementation has no "memory": one line of
interactive input has no effect on the next. That could be improved.

Telling ``rstweaver`` about the language
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you have defined a language, you will need to register its directives.
This is a matter of calling

::
    
    rstweaver.register_weaver_language(MyLanguage)

sometime before you process your document.

Of course, if you're using the ``rstweave`` program that won't do you much
good. For ``rstweave`` to see the language, you need to add it to the
``rstweaver`` distribution.

Adding a language to ``rstweaver`` proper
-----------------------------------------

1. Add the code for you language in ``rstweaver/languages/``
2. Import it from ``rstweaver/languages/__init__.py`` and add it to the
   obvious list.

Now ``rstweave`` will recognize it. Yes this is a terrible system. I just
haven't gotten around to making a better one.

