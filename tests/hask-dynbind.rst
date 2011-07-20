
.. GHC's dynamic binding is nice but it isn't really Haskell

With `appropriate
options <http://www.haskell.org/ghc/docs/6.12.1/html/users_guide/other-type-extensions.html>`_,
GHC let's you do something like:

.. haskell:: imp-params.hs exec
    
    {-# LANGUAGE ImplicitParams #-}
    
    main = do
        let exp = ?x + ?y
        print exp where
            ?x = 3
            ?y = 7

If you look at the type of `?x + ?y` you can see that the unbound variables are
reflected in the type.

.. haskell:: imp-params.hs restart
    
    {-# LANGUAGE ImplicitParams #-}
    {-# LANGUAGE NoMonomorphismRestriction #-}
    
    dexp = ?x + ?y

.. blank

.. ghci:: imp-params.hs

    :t dexp

(Sorry about lifting the monomorphism restriction -- I didn't want to add a
type signature because that would defeat the whole point of inspecting the type
with ``ghci``).

I like this feature, but it's not really in the spirit of Haskell. Though they
did do a good job of covering up the problems; if you look at that type
signature you'll see that, even though ``dexp`` takes parameters, it does not
have a function type: it has the type of its result. This is important because

.. ghci::

    :t (+)

In particular, if ``?x`` were a function type (like the name "implicit
parameters" suggests), you would *not* be allowed to use ``+`` on it. But you
can see that this is deceptive...

.. haskell:: deceptive.hs

    {-# LANGUAGE ImplicitParams #-}
    
    dexp :: (?x::Int) => Int
    dexp = ?x

.. ghci:: deceptive.hs

    :t dexp
    print dexp

If it were really just an Int as its type claims, you should be allowed to
print it. But if it's not really just an Int you should not be allowed to use
``+`` on it.

(Actually technically you *are* allowed to print it, which is why I had to use
``ghci`` to get that error:

.. haskell:: deceptive.hs redo exec

    {-# LANGUAGE ImplicitParams #-}
    
    dexp :: (?x::Int) => Int
    dexp = ?x
    
    main = do
        print dexp

You see the unbound variables leaked all the way out in to main, changed its
type, and hit the monorphism restriction. Sneaky.)

Haskell has of course encountered this dilemma before, which is where functors
come from. And in functors the decision was that it is better to make the magic
explicit.

.. haskell:: params-with-functors.hs
    
    dexp :: Int -> Int
    dexp = id
    
    instance Functor ((->) a) where
        fmap f p = f . p
    
.. ghci:: params-with-functors.hs

    :t fmap (5-) dexp
    fmap (5-) dexp 3

It's just like an implicit (unnamed) parameter, except it doesn't leak up the
call stack by itself -- you have to do so explicitly with ``fmap``.

But whether or not we're ok with this breach of Haskellinity is really beside
the point: you can't do that much with implicit parameters anyway. As I pointed
out `last time
<http://strugglingthroughproblems.blogspot.com/2011/07/pretending-in-haskell.html>`_
you have no runtime access to implicit parameters, so you can't do anything
like R's ``with()``, which would really be the biggest use for dynamic binding.

But this is Haskell, surely we can implement dynamic binding!

Since an "unbound expression" is basically a map from a named set of parameters
to its resulting value, we could represent it as a map taking an ``HList``
``Record``.

.. haskell:: dyn-bind.hs
    :name: defs

    {-# LANGUAGE EmptyDataDecls #-}
    {-# LANGUAGE TemplateHaskell #-}
    {-# LANGUAGE DeriveDataTypeable #-}

    import Data.HList
    import Data.HList.Label4
    import Data.HList.TypeEqGeneric1
    import Data.HList.TypeCastGeneric1
    import Data.HList.MakeLabels

    $(makeLabels ["labX", "labY"])

    x rec = rec # labX
    y rec = rec # labY
    
    z rec = (x rec) + (y rec)

Here ``x`` represents ``?x``, ie it takes the supplied variables and just grabs
the one called ``x``. Likewise for ``y``. Then ``z`` represents ``?x + ?y``.
These have types:

.. ghci:: dyn-bind.hs

    :t x
    :t y
    :t z

And we can bind them:

.. haskell:: dyn-bind.hs exec
    :name: main

    bindings =
        labX .=. 5 .*.
        labY .=. 7 .*.
        emptyRecord
    
    main = do
        print $ x bindings
        print $ y bindings
        print $ z bindings

And rebind them:

.. haskell:: dyn-bind.hs redo exec
    :name: main

    b1 =
        labX .=. 5 .*.
        labY .=. 7 .*.
        emptyRecord

    b2 =
        labX .=. 9 .*.
        labY .=. 12 .*.
        emptyRecord
    
    main = do
        print $ z b1
        print $ z b2

So that's all the structure we need; now we just need ways to combine them.
Here you can see we are going to run into problems, because if we start with
say ``+``, which is ``(Num a) => a -> a -> a``, and bind it to its first
dynamic argument, we will get a dynamic function. Meaning the seconding binding
has a different type signature. Or, as an example,

.. haskell:: dyn-bind.hs
    :name: combine
    :after: defs
    
    call1 f dexp rec = f (dexp rec)

.. ghci:: dyn-bind.hs

    :t (+)
    :t call1 (+) x
    :t call1 (bind1 (+) x) y

That does not look at all like the right type. And of course binding it fails:

.. ghci:: dyn-bind.hs

    (call1 (call1 (+) x) y) b1

So the second binding is a different type...

.. haskell:: dyn-bind.hs redo
    :name: combine
    
    call1 f dexp rec = f (dexp rec)
    call2 f dexp rec = (f rec) (dexp rec)

.. ghci:: dyn-bind.hs

    (call2 (call1 (+) x) y) b1

