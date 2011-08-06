
.. weaver:: exec new join

    first
    
    .. cpp:: foo.h
    
        #ifndef _foo_h
        #define _foo_h 1
    
        int foo();
        
        #endif /* defined _foo_h */
    
    .. cpp:: foo.cpp
    
        #include "foo.h"
    
        int foo() {
            return 5;
        }
    
.. weaver:: exec new join

    next
    
    .. icpp:: foo.h foo.cpp
        
        std::cout << foo() << "\n"


