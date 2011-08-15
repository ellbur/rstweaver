
.. It's important to test these so we know that the
.. example language definitions are correct.

.. minhaskell:: exec

    main = do
        print "Hi"

.. minghci::
    
    [x | (x:_) <- ["a", "b", ""]]

