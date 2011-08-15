
.. haskell:: Main.hs

    <<<Imports>>>
    
    <<<Functions>>>
    
    main = do
        <<<Main>>>

.. haskell:: Main.hs
    :in: Imports
    
    import Control.Monad.Reader
    import Control.Monad.Identity

.. haskell:: Main.hs
    :in: Functions
    
    foo :: ReaderT Int Identity Int
    foo = do
        x <- ask
        return $ x + 7
    
.. haskell:: Main.hs
    :in: Main
    
    --
        print $ runIdentity $ runReaderT foo 5

.. haskell:: Main.hs exec


