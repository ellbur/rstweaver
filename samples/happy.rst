
.. happy:: Parser.y exec

    {
    module Parser where
    }
    
    %name      parse
    %tokentype { Char }
    
    %token
        a    { 'a' }
        b    { 'b' }
    
    %%
                      
    File : AB { $1 }
    
    AB :        { (0::Int)      }
       | a AB b { (1::Int) + $2 }
    
    {
    
    happyError _ = error "Happy error!"
    
    }

.. haskell:: Main.hs exec

    import Parser
    
    main = do
        let text = "aaabbb"
        print $ parse text


