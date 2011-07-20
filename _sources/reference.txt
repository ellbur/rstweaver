
Directives Reference
====================

This reference is about using the directives: options and arguments that they
accept. For the API documentation, see... somewhere.

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

Commands
--------

Commands are distinguished from the file name by the absence of a '.' in their
name. I realize this is not the best system.

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
    possible

noecho
    Don't print the code.

block
    When execing, only include ouput from this one block. The language might
    not support this (it probably doesn't).

Interactive directive
~~~~~~~~~~~~~~~~~~~~~

Arguments
~~~~~~~~~

File names to be "imported" before starting the interactive session. These
refer to files written in previous non-interactive blocks.

Options
~~~~~~~

None.

