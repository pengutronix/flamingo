

Basic Concepts
==============

Context
-------

The ``flamingo.core.context.Context`` object holds all runtime state, with all
settings, loaded plugins and media informations. It gets passed into every
plugin hook and is available in every rendered template and content object.


Content / ContentSet
--------------------

``flamingo.core.data_model.Content`` objects are the main data store for user
content. Multiple ``flamingo.core.data_model.Content`` objects are stored in a
``flamingo.core.data_model.ContentSet``.

All content that is supposed to be written to the output should be a
``flamingo.core.data_model.Content``. You are not supposed to write to the
output directly.

Content objects can be created by parsing a content file or by using
``flamingo.core.data_model.Content.add()``.


Plugins / Hooks
---------------

Plugins are meant to extend flamingo or to modify the flamingo context while
building. Plugins or hooks are the only places where you supposed to write
python code.


Media- and Static Files
-----------------------

Media files are part of the user content and are stored in ``CONTENT_ROOT``.
They get copied to the output only if they get referenced somewhere.

Static files get copied in every build, no matter if they get used or not.

A vacation photo for a blog post would be media file. The logo of your blog
would be a static file.


Theme
-----

A flamingo theme consists of HTML, CSS, JS and other assets only. A theme does
not contain python code.
