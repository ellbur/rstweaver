
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
come from. And in functors the magic is always made explicit:

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
    :t call1 (call1 (+) x) y

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

It is of course totally contrary to the spirit of dynamic binding to require
the programmer to pay such close attention to whether this is the first or
second or any dynamic combination. And this is where things start to fall
apart...

The natural way to make the ``call`` operation generalize the signatures of
``call1`` and ``call2`` would be to use a typeclass:

.. haskell:: dyn-bind2.hs

    {-# LANGUAGE EmptyDataDecls #-}
    {-# LANGUAGE TemplateHaskell #-}
    {-# LANGUAGE DeriveDataTypeable #-}
    {-# LANGUAGE MultiParamTypeClasses #-}
    {-# LANGUAGE FunctionalDependencies #-}
    {-# LANGUAGE FlexibleInstances #-}

    import Data.HList
    import Data.HList.Label4
    import Data.HList.TypeEqGeneric1
    import Data.HList.TypeCastGeneric1
    import Data.HList.MakeLabels

    $(makeLabels ["labX", "labY"])

.. haskell:: dyn-bind2.hs join
    :name: class

    class Call a b c | a b -> c where
        call :: a -> b -> c

.. haskell:: dyn-bind2.hs join
    
    infixl <*>
    f <*> x = call f x
    
    instance Call (a -> b) a b where
        call f x = f x

Which gets us regular function application, sort of:

.. ghci:: dyn-bind2.hs

    ((+) :: Int -> Int -> Int) <*> (2::Int) <*> (3::Int)
    (+) <*> 2 <*> 3

It performs correctly but we utterly and completely lose type inference,
because the typeclass needs things very specific before it is willing to
do anything.

Note that if we were looking for just regular no dynamic binding Haskell
we could have written the functional dependency

.. haskell:: dyn-bind2.hs redo
    :name: class

    class Call a b c | a -> b c where
        call :: a -> b -> c

And now we have type inference again,

.. ghci:: dyn-bind2.hs

    (+) <*> 2 <*> 3

But that won't work if ``(+)`` shoul be able to be applied both to dynamic and
to not-dynamic expressions.

I wrestled with a few other variations on this path -- I don't think it's the
right way to go. As with most things in Haskell the most reliable way to deal
with ambiguity is to make things more explicit. And here that means that every
little node in the formuala tree should be decorated to show what its dynamic
variables are.




.. haskell:: dyn-bind3.hs

    {-# LANGUAGE EmptyDataDecls #-}
    {-# LANGUAGE TemplateHaskell #-}
    {-# LANGUAGE DeriveDataTypeable #-}

    module DynBind where

    import Data.HList hiding (apply,Apply)
    import Data.HList.Label4
    import Data.HList.TypeEqGeneric1
    import Data.HList.TypeCastGeneric1
    import Data.HList.MakeLabels
    
    $(makeLabels ["labX", "labY"])

So we make it explicit that this is a dynamically bindable expression:

.. haskell:: dyn-bind3.hs

    data DynExp a b = DynExp (a -> b)

A ``leaf`` is an expression with no dynamic variables:

.. haskell:: dyn-bind3.hs

    leaf x = DynExp (\t -> x)

And then ``dynVar`` introduces one variable:

.. haskell:: dyn-bind3.hs

    dynVar label = DynExp grab where
        grab rec = rec # label

When we combine expressions by applying, we may as well just pass the whole
record on to both branches: they'll just ignore the fields they don't need
(exercise: why is this a bad idea?):

.. haskell:: dyn-bind3.hs

    apply (DynExp f) (DynExp x) = DynExp g where
        g rec = (f rec) (x rec)

    infixl <*>
    a <*> b = apply a b

    with hl (DynExp f) = f hl

So let's test that...

.. haskell:: dyn-bind3.hs exec
    :name: main
    
    expr = (leaf (+)) <*> (dynVar labX) <*> (dynVar labY)
    bindings =
        labX .=. 5 .*.
        labY .=. 3 .*.
        emptyRecord

    main = do
        print $ with bindings expr

So far it seems to work. But then problems develop...

.. haskell:: dyn-bind3.hs redo exec
    :name: main
    
    expr = (leaf (+)) <*> (dynVar labX) <*> (dynVar labY)
    b1 =
        labX .=. 5 .*.
        labY .=. 3 .*.
        emptyRecord
    b2 =
        labY .=. 3 .*.
        labX .=. 5 .*.
        emptyRecord

    main = do
        print $ with b1 expr
        print $ with b2 expr

That's a tricky one. So does it matter what order you specify the labels in?

.. haskell:: dyn-bind3.hs redo exec
    :name: main
    
    expr = (leaf (+)) <*> (dynVar labX) <*> (dynVar labY)
    b1 =
        labX .=. 5 .*.
        labY .=. 3 .*.
        emptyRecord
    b2 =
        labY .=. 3 .*.
        labX .=. 5 .*.
        emptyRecord

    main = do
        print $ with b2 expr

No... it just won't work if you do it 2 different ways. What is going on here?
What if you don't specify them any ways?

.. haskell:: dyn-bind3.hs redo exec
    :name: main
    
    expr = (leaf (+)) <*> (dynVar labX) <*> (dynVar labY)

    main = do
        print "hi"

And now it becomes apparent... notice that this works:

.. haskell:: dyn-bind3.hs redo exec
    :name: main
    
    expr rec = with rec $ (leaf (+)) <*> (dynVar labX) <*> (dynVar labY)

    main = do
        print "hi"

In other words it would appear that we have hit the monomorphism restriction ;)

We could just lift the restriction, but I prefer another approach that makes
types more explicit all around:

.. haskell:: dyn-bind4.hs

    {-# LANGUAGE FlexibleContexts #-}
    {-# LANGUAGE EmptyDataDecls #-}
    {-# LANGUAGE TemplateHaskell #-}
    {-# LANGUAGE DeriveDataTypeable #-}

    import Data.HList hiding (apply,Apply)
    import Data.HList.Label4
    import Data.HList.TypeEqGeneric1
    import Data.HList.TypeCastGeneric1
    import Data.HList.MakeLabels
    
    $(makeLabels ["labX", "labY"])

    data DynExp a b = DynExp (a -> b)

Leaves explicitly take no parameters:

.. haskell:: dyn-bind4.hs

    leaf :: v -> DynExp (Record HNil) v
    leaf x = DynExp (\t -> x)

dynVars explicitly take just one:

.. haskell:: dyn-bind4.hs

    dynVar :: label -> DynExp (Record (HCons (LVPair label v) HNil)) v
    dynVar label = DynExp grab where
        grab (Record (HCons (LVPair v) HNil)) = v

And ``apply`` uses the functional dependency in ``HLeftUnion`` to give its
result an explicit type as well (which is why we have to give an explicit type
signature, which is why we have to specify all that other stuff):

.. haskell:: dyn-bind4.hs

    apply (DynExp f) (DynExp x) = DynExp (splitApply f x)

    splitApply :: (
            HLeftUnion (Record hl1) (Record hl2) (Record hlU),
            H2ProjectByLabels ls1 hlU hl1' uu1,
            H2ProjectByLabels ls2 hlU hl2' uu2,
            HRearrange ls1 hl1' hl1,
            HRearrange ls2 hl2' hl2,
            HLabelSet ls1,
            HLabelSet ls2,
            HRLabelSet hl1',
            HRLabelSet hl2',
            RecordLabels hl1 ls1,
            RecordLabels hl2 ls2
        ) =>
        (Record hl1 -> a -> b) ->
        (Record hl2 -> a) ->
        Record hlU ->
        b
    splitApply f x hl = f (hMoldByType hl) (x (hMoldByType hl))

And my favorite are these infinitily recursive adaptor functions:

.. haskell:: dyn-bind4.hs

    hProjectByType r1 = r2 where
        r2 = hProjectByLabels r2Labels r1
        r2Labels = recordLabels r2

    hMoldByType r1 = r2 where
        r2 = hRearrange r2Labels $ hProjectByLabels r2Labels r1
        r2Labels = recordLabels r2

    infixl <*>
    a <*> b = apply a b

    with hl (DynExp f) = f $ hMoldByType hl

And now everything works:

.. haskell:: dyn-bind4.hs exec
    :name: main
    
    expr = (leaf (+)) <*> (dynVar labX) <*> (dynVar labY)
    b1 =
        labX .=. 5 .*.
        labY .=. 3 .*.
        emptyRecord
    b2 =
        labY .=. 3 .*.
        labX .=. 5 .*.
        emptyRecord

    main = do
        print $ with b1 expr
        print $ with b2 expr

This is of course an extremely ugly way to write expressions, but since we're
already using Template Haskell we may as well use Template Haskell.

.. haskell:: DynBind.hs noecho done

    {-# LANGUAGE FlexibleContexts #-}
    {-# LANGUAGE EmptyDataDecls #-}
    {-# LANGUAGE TemplateHaskell #-}
    {-# LANGUAGE DeriveDataTypeable #-}

    module DynBind where

    import Data.HList hiding (apply,Apply)
    import Data.HList.Label4
    import Data.HList.TypeEqGeneric1
    import Data.HList.TypeCastGeneric1
    import Data.HList.MakeLabels

    data DynExp a b = DynExp (a -> b)

    leaf :: v -> DynExp (Record HNil) v
    leaf x = DynExp (\t -> x)

    dynVar :: label -> DynExp (Record (HCons (LVPair label v) HNil)) v
    dynVar label = DynExp grab where
        grab (Record (HCons (LVPair v) HNil)) = v

    apply (DynExp f) (DynExp x) = DynExp (splitApply f x)

    splitApply :: (
            HLeftUnion (Record hl1) (Record hl2) (Record hlU),
            H2ProjectByLabels ls1 hlU hl1' uu1,
            H2ProjectByLabels ls2 hlU hl2' uu2,
            HRearrange ls1 hl1' hl1,
            HRearrange ls2 hl2' hl2,
            HLabelSet ls1,
            HLabelSet ls2,
            HRLabelSet hl1',
            HRLabelSet hl2',
            RecordLabels hl1 ls1,
            RecordLabels hl2 ls2
        ) =>
        (Record hl1 -> a -> b) ->
        (Record hl2 -> a) ->
        Record hlU ->
        b
    splitApply f x hl = f (hMoldByType hl) (x (hMoldByType hl))

    -- Can you believe this works?
    hMoldByType r1 = r2 where
        r2 = hRearrange r2Labels $ hProjectByLabels r2Labels r1
        r2Labels = recordLabels r2

    infixl <*>
    a <*> b = apply a b

    extract (DynExp f) = f emptyRecord

    bind label value (DynExp f) = DynExp g where
        g hl = f ((label .=. value) .*. hl)

    with hl (DynExp f) = f $ hMoldByType hl

.. haskell:: Leafify.hs done

    {-# LANGUAGE EmptyDataDecls #-}
    {-# LANGUAGE TemplateHaskell #-}
    {-# LANGUAGE DeriveDataTypeable #-}

    module Leafify where

    import DynBind

    import Language.Haskell.TH
    import Language.Haskell.TH.Quote
    import Language.Haskell.Meta.Parse
    import Data.List.Utils

    var str = VarE (mkName str)
    vLeaf   = var "leaf"
    vDynVar = var "dynVar"
    vApply  = var "apply"
    vFlip   = var "flip"

    fromRight (Right x) = x

    lf = QuasiQuoter {
        quoteExp = doLf,
        quotePat = doLfPat
    }

    -- Not used, but will warn if we don't provide it.
    doLf :: String -> Q Exp
    doLf str = do
        return $ leafify' $ fromRight $ parseExp str

    doLfPat :: String -> Q Pat
    doLfPat str = do
        return $ WildP

    infixl <**>
    a <**> b = AppE a b

    -- This isn't really the best way to do things; we should really
    -- do all of this in the Q monad. But this is flatter ;)
    leafify' :: Exp -> Exp
    leafify' (VarE v) =
        let name = nameBase v in
            if startswith "lab" name
            then vDynVar <**> (VarE v)
            else vLeaf <**> (VarE v)
    leafify' (ConE x) = vLeaf <**> (ConE x)
    leafify' (LitE x) = vLeaf <**> (LitE x)
    leafify' (AppE f x) = vApply <**> (leafify' f) <**> (leafify' x)
    leafify' (InfixE Nothing op Nothing) =
        vLeaf <**> (InfixE Nothing op Nothing)
    leafify' (InfixE (Just a) op Nothing) = expr where
        expr = vApply <**> (vLeaf <**> f) <**> (leafify' a)
        f    = InfixE Nothing op Nothing
    leafify' (InfixE Nothing op (Just b)) = expr where
        expr = vApply <**> (vLeaf <**> f) <**> (leafify' b)
        f    = vFlip <**> (InfixE Nothing op Nothing)
    leafify' (InfixE (Just a) op (Just b)) = expr where
        expr  = vApply <**> expr1 <**> (leafify' b)
        expr1 = vApply <**> (vLeaf <**> f) <**> (leafify' a)
        f     = InfixE Nothing op Nothing
    leafify' (LamE ps x) = LamE ps (leafify' x)
    leafify' (TupE xs) = TupE (fmap leafify' xs)
    leafify' (CondE x y z) =
        CondE (leafify' x) (leafify' y) (leafify' z)
    leafify' (ListE xs) = ListE (fmap leafify' xs)

    -- Not Implemented
    --leafify' (LetE d x)
    --leafify' (CaseE x m)
    --leafify' (DoE sts)
    --leafify' (CompE sts)
    --leafify' (ArithSeqE r)
    --leafify' (SigE x t)
    --leafify' (RecConE n fes)
    --leafify' (RecUpdE x fes)

So that we can write

.. haskell:: dyn-bind5.hs exec

    {-# LANGUAGE TemplateHaskell #-}
    {-# LANGUAGE QuasiQuotes #-}
    {-# LANGUAGE EmptyDataDecls #-}
    {-# LANGUAGE DeriveDataTypeable #-}

    import Leafify
    import DynBind

    import Data.HList hiding (apply,Apply)
    import Data.HList.Label4
    import Data.HList.TypeEqGeneric1
    import Data.HList.TypeCastGeneric1
    import Data.HList.MakeLabels

    $(makeLabels ["labX", "labY", "labZ"])

    expr = [$lf|
            (labX + labY) * labX - labZ/2
        |]

    bindings =
        labX .=. 5 .*.
        labY .=. 7 .*.
        labZ .=. 10 .*.
        emptyRecord

    main = do
        print $ with bindings expr

Man that is hacky... but it works.

.. ghci::

    5

