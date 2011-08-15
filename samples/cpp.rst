
.. cpp:: foo.h

    #ifndef _foo_h
    #define _foo_h 1
    
    int foo(int x);
    
    #endif

.. cpp:: foo.c

    #include "foo.h"
    
    int foo(int x) {
        return (x*7) ^ (x + 13131) ^ (x*x + x + 51335);
    }

.. icpp:: foo.h foo.c

    std::cout << foo(0)
    std::cout << foo(1)
    std::cout << foo(2)

