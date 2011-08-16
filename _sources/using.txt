
Using ``rstweaver``
===================

.. contents::

Using the directives
~~~~~~~~~~~~~~~~~~~~

Sphinx
------

Add to your ``conf.py``:

::

    import rstweaver
    rstweaver.register_all_languages()

To get the necessary CSS, run::

    rstweave --print-css

And add it somewhere that Sphinx will include (such as at the end of
``default.css``)

To register your own languages

::
    
    rstweaver.register_weaver_language(MyLanguage)

This same steps should work for any tool built on ``docutils``.

``rstweave``
------------

``rstweave`` is a small program much like ``rst2*`` that reads in an rst
document and outputs a target format, with the ``rstweaver`` directives
registered.

Some examples
~~~~~~~~~~~~~

The examples here are produced with ``rstweaver``. It is literate literate
programming. That means you'll see a block of raw reST code, followed by the
rendered HTML it should produce. That block of course has embedded blocks of
code in it, which I have tried to distinguish using thinner lines. Hope you can
follow.

There are far far more examples over at :doc:`examples`.

Let's make a Haskell program:

.. weaver:: new exec join

    .. haskell:: Whatup.hs exec
        
        main = do
            putStrLn "Hello... world."

And that's the simplest non-nil thing you can do with ``rstweaver``.

Note the command ``exec`` which tells rstweaver to execute this file. If we
omit it:

.. weaver:: new exec join

    .. haskell:: NotWritten.hs
    
        main = do
            putStrLn "Stuff to say, but will never be said."
            
That fed some content to the file but it didn't execute it or even compile it.

A file can be built in multiple stages:

.. weaver:: new exec join

    .. haskell:: Stages.hs
    
        import Control.Monad
    
    .. haskell:: Stages.hs
    
        genNumbers :: [Int]
        genNumbers = do
            a <- [0, 1]
            b <- [0, 1]
            return $ a + b
    
    .. haskell:: Stages.hs exec
    
        main = do
            print genNumbers

The last stage included "``exec``", so the file was executed.

You can name the stages:

.. weaver:: new exec join

    .. haskell:: Named.hs
        :name: imports
        
        import Control.Monad

And then go back and edit them:

.. weaver:: new exec join

    .. haskell:: Named.hs redo
        :name: imports
        
        import Control.Monad
        import Control.Applicative

Or insert a stage after a named stage:

.. weaver:: new exec join

    .. haskell:: Named.hs
        :after: imports
        
        x = 5

Or at the beginning:

.. weaver:: new exec join

    .. haskell:: Named.hs
        :after: start
        
        {-# LANGUAGE DeriveDataTypeable #-}

You can restart a whole file:

.. weaver:: new exec join

    .. haskell:: Main.hs restart
        
        main = do
            putStrLn "Hello... world?"

You can run interactive commands that reference your file:

.. weaver:: new exec join

    .. ghci:: Main.hs
        
        :t main
 
Error messages do not interrupt the execution: they will show up as error
messages in the resulting HTML. I like this because it lets you show what error
messages look like. You may or may not approve.

