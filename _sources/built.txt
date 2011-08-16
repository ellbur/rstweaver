
Accessing built files
=====================

When editing ``foo.rst``, the files produced by ``rstweaver`` will go in ``foo.rst-weaver/``.
They are only created as needed; to force them to be created add

.. weaver:: new noeval join

    .. write-all::

to the end of your document.

