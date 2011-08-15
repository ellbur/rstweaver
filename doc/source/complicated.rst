
Even more complicated examples
==============================

.. contents::

Producing a file then reading it in
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Producing a file
----------------

.. weaver:: new exec join

    .. ibash::

        cat /proc/meminfo > some-text
        head some-text

Reading it
----------

We'll do a letter frequency count.

.. weaver:: new exec join

    .. python:: new exec

        with open('some-text') as hl:
            content = hl.read()
        
        content = content.lower()
        content = filter(
            lambda c: ord('a') <= ord(c) <= ord('z'),
            content
        )
        
        table = { }
        
        for c in content:
            now = table.get(c, 0)
            now += 1
            table[c] = now
        
        pairs = table.items()
        pairs.sort(key = lambda p: -p[1])
        for letter, count in pairs:
            print('%s %3d' % (letter, count))

Preprocessing a source file
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Happy
-----

`Happy <http://haskell.org/happy/>`_ is a parser generator for Haskell. It is
run through the ``happy`` preprocessor to produce a Haskell module.

Making the happy file
.....................

.. weaver:: new exec join

    .. happy:: Counter.y
    
        {
        module Counter where
        }
        
        %name      count
        %tokentype { Char }
        
        %token
            x   { _ }
        
        %%
                          
        File : Xs { $1 }
        
        Xs :      { (0::Int)      }
           | Xs x { (1::Int) + $1 }
        
        {
        happyError _ = error "Happy error!"
        }

Preprocessing
.............

(This could have been done in the same step):

.. weaver:: new exec join

    .. happy:: Counter.y exec
        
Using it
........

.. weaver:: new exec join

    .. haskell:: Main.hs exec
    
        import Counter
    
        main = do
            let text = "It rained all day."
            print $ count text

.. _arbfiles:

Working with arbitrary files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because ``rstweaver`` has a ``bash`` directive, you can do pretty much anything
with it, even if ``rstweaver`` itself doesn't understand the language you're
working in. For example, ``rstweaver`` doesn't do Perl, but that's no
limitation:

.. weaver:: new exec join

    .. file:: no-es.pl
        :highlight: perl
        
        #!/usr/bin/perl
        
        while (<>) {
            s/e//gi;
            print;
        }
    
    .. ibash::
    
        chmod a+x no-es.pl
        ./no-es.pl < /proc/meminfo | head


