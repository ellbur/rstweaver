
rstweaver
=========

``rstweaver`` is a framework for building reST directives that support literate
programming, in a style similar to `Sweave
<http://www.stat.uni-muenchen.de/~leisch/Sweave/>`_.

Rather than the typical "document is a source file" model, in ``rstweaver`` a
document *manages* source files -- several of them, in possibly multiple
languages. They can be built, executed, changed, reexecuted. This has both
advantages and disadvantages, but it is nearly essential for very static
compiled languages to be nice in literate code.

Nice features:

- These are just ``reST`` directives -- they will integrate into any system
  that uses reST. ``rstweaver`` itself is documented using ``rstweaver`` in
  `Sphinx <http://sphinx.pocoo.org/>`_.
  
- Largely language agnostic. It knows about Haskell, Happy, Python, Bash, C++
  and reST, but because it does bash you can use practically any language.
  
- Because it is pure docutils, it should be possible to produce output in any
  format that docutils supports.
  
- Results are cached and dependencies tracked in a fashion similar to an
  incremental build tool such as ``make``, which makes repeated runs go much
  faster.

- It supports a syntax similar to `noweb <http://www.cs.tufts.edu/~nr/noweb/>`_
  for structuring a source file and then filling in the parts.

Features which are noticeably missing:

- Plots
  
Contents:

.. toctree::
    :maxdepth: 2

    dependencies
    installing
    using
    examples
    complicated
    built
    caching
    languages
    reference

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

