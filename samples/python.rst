
The problem with varargs in python:

.. python:: exec

    class A:
        
        def withx(x):
            def decorator(handler):
                def decorated(**args):
                    args['x'] = x
                    return handler(**args)
                return decorated
            return decorator
        
        @withx(5)
        def foo(self, x, y):
            return x + y

    a = A()
    print(a.foo(y = 7))

Some sequences:

.. ipython::

    a = [1] * 10
    a
    b = [sum(a[:(i+1)]) for i in range(len(a))]
    b
    c = [sum(b[:(i+1)]) for i in range(len(b))]
    c

