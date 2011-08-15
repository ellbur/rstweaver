
Directives Reference
====================

This reference is about using the rst directives: options and arguments that
they accept. For the API documentation, see... somewhere.

To get a feel for how to use these directives, see the :doc:`tutorial`.

Non-interactive directive
~~~~~~~~~~~~~~~~~~~~~~~~~

Arguments
---------
    
Commands and optionally a file name, in any order. See below for details.

Options
-------

name
    A name for this code block.

after
    Place this block after the named block. Use ``start`` to make this the
    first block in the file. If omitted, block will be added at the end.

in
    Place this block into a named block as a sub-block. Usually used with
    :ref:`nowebish`.

Commands
--------

exec
    After appending the block, run this file.

done
    After appending the block, compile and test for errors/warnings.

restart
    Before appending the block, erase the file and start again.

noeval
    Don't add this block to the file.

redo
    Replace a named block with new content.

join
    Try to get this block as visually close to the preceding content as
    possible.

noecho
    Don't print the code.

new
    Invent a unique file name.

recall
    Print the contents of a named block.

Interactive directive
~~~~~~~~~~~~~~~~~~~~~

Arguments
~~~~~~~~~

File names to be "imported" before starting the interactive session. These
refer to files written in previous non-interactive blocks.

Options
~~~~~~~

None.

