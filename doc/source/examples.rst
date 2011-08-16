
Examples
~~~~~~~~

.. contents::

Editing
-------

The primary purpose of ``rstweaver`` is to be able to edit source files from
the ``rst`` document.

Naming a block
..............

.. weaver:: new exec join

    .. cpp:: main.cpp done
        :name: includes
        
        #include <iostream>
        #include <cstdlib>

Appending
.........

.. weaver:: new exec join

    .. cpp:: main.cpp done
        :name: main
        
        int main() {
            std::cout << ::time(0) << "\n";
        }

Inserting
.........

.. weaver:: new exec join

    .. cpp:: main.cpp done
        :after: includes
        
        int even_time() {
            int time;
            for (;;) {
                time = ::time(0);
                if (time % 2 == 0) return time;
                
                sleep(1);
            }
        }

Editing
.......

.. weaver:: new exec join

    .. cpp:: main.cpp redo exec
        :name: includes
        
        #include <iostream>
        #include <ctime>
        #include <cstdlib>

Deleting
........

Uh... you can't do this right now. You can set its contents to nothing, though.

.. weaver:: new exec join

    .. cpp:: main.cpp redo
        :name: main

.. _nowebish:

Noweb-like structuring
----------------------

One of the features that ``rstweaver`` borrows from ``noweb`` is the ability to
define the structure of a file and then fill in the parts. For example if we
are using Happy we can make a skeleton:

.. weaver:: new exec join

    .. happy:: Parser.y
    
        {
        module Parser where
        }
        
        <<<<Configuration>>>>
        
        <<<<Tokens>>>>
        
        %%
        
        <<<<Rules>>>>
        
        {
        <<<<Haskell Code>>>>
        }
    
    .. happy:: Parser.y
        :in: Configuration
        
        %name      parse
        %tokentype { Char }
        
    .. happy:: Parser.y
        :in: Tokens
        
        %token
            a    { 'a' }
            b    { 'b' }
    
    .. happy:: Parser.y
        :in: Rules
        
        File : AB { $1 }
        
        AB :        { (0::Int)      }
           | a AB b { (1::Int) + $2 }
    
    .. happy:: Parser.y
        :in: Haskell Code
        
        happyError _ = error "Happy error!"

Showing already-written blocks
------------------------------

.. weaver:: new exec join

    .. cpp:: main.cpp recall
        :name: includes

C++
---

Noninteractive
..............

.. weaver:: new exec join

    .. cpp:: new exec
    
        #include <iostream>
    
        int main() {
            static const int N = 20;
            int x[N];
            
            using std::cout;
            
            for (int i=0; i<N; i++) {
                x[i] = 1;
            }
            
            for (int j=0; j<N; j++) {
                for (int i=1; i<N; i++) {
                    x[i] = 3*x[i-1] - x[i];
                }
            }
        
            for (int i=0; i<N; i++) {
                cout << x[i] << "\n";
            }
        }

Interactive
...........

.. weaver:: new exec join

    .. icpp::
    
    	int x = 5
    	std::cout << x

Which isn't terribly handy unless you want to use some code you've written:

.. weaver:: new exec join

    .. cpp:: collatz.hpp
    
        int collatz(int n);

    .. cpp:: collatz.cpp
    
        int collatz(int n) {
            int k = n;
            int count = 0;
            
            while (k != 1) {
                if (k % 2 == 0) k = k/2;
                else k = 3*k + 1;
                
                count++;
            }
            
            return count;
        }
    
    .. icpp:: collatz.cpp collatz.hpp
    
    	std::cout << collatz(1)
    	std::cout << collatz(2)
    	std::cout << collatz(3)
    	std::cout << collatz(4)
        std::cout << collatz(5)

Unfortunately every interactive line has to be one file line (because to do
otherwise would require parsing the C++) so this fails:

.. weaver:: new exec join

    .. icpp::
    
        for (int i=0; i<10; i++) {
            std::cout << i;
        }

Python
------

Non-interactive
...............

.. weaver:: new exec join

    .. python:: new exec
    
        import numpy as np
        
        x = np.random.uniform(size=20)
        print(np.mean(x))
        print(np.std(x))

Interactive
...........

.. weaver:: new exec join
    
    .. ipython::
        
        import numpy as np
        x = np.random.uniform(size=20)
        print(np.mean(x))
        print(np.std(x))

Haskell
-------

Non-interactive
...............

.. weaver:: new exec join

    .. haskell:: new exec
    
        {-# LANGUAGE OverlappingInstances #-}
        {-# LANGUAGE FlexibleInstances #-}
        {-# LANGUAGE ScopedTypeVariables #-}
        
        class CountArgs a where
            countArgs :: a -> Int
        
        instance (CountArgs b) => CountArgs (a -> b) where
            countArgs _ = (1::Int) + (countArgs (undefined :: b))
        
        instance CountArgs a where
            countArgs _ = (0::Int)
        
        main = do
            print $ countArgs (:)

Interactive
...........

.. weaver:: new exec join

    .. ghci::
        
        :i Show

