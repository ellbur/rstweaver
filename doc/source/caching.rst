
Caching
=======

``rstweaver`` caches the results of program runs. It also watches for
dependencies and modifications, so *usually* the caching is invisible to the
user and things just "go faster".

However, occasionally due to a bug in ``rstweaver`` or a dependency it can't
see, an incorrect result will be cached and held on to. When this happens,
delete the cache file (see below), and report it as a bug.

One situation where this is likely to happen is when a file becomes a
dependency because of its *absence* rather than its presence. For example,

.. cpp:: bad-cache.c exec

    #include "not-exist.h"

since ``not-exist.h`` doesn't exist, ``gcc`` dies on compiling. However, if
``not-exist.h`` is created, that will change the result of the run, but
``rstweaver`` won't know that: it never saw anyone access ``not-exist.h`` so it
has no way of knowing that that is a dependency.

The cache file
~~~~~~~~~~~~~~

When editing ``foo.rst`` the cache file is ``foo.rst-weaver/cache``.

