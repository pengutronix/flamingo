

Shell
=====

.. code-block:: txt

	fsc@joshua:work/devel/flamingo/doc$ make shell
	. env/bin/activate && \
	flamingo shell -s settings.py menu.py
	Python 3.7.3 (default, Feb  8 2020, 18:24:17)
	Type 'copyright', 'credits' or 'license' for more information
	IPython 6.5.0 -- An enhanced Interactive Python. Type '?' for help.

	In [1]: context
	Out[1]: <flamingo.core.context.Context at 0x7fdeb0196d68>

	In [2]:


**For this feature IPython needs to be installed. Read the
"Optional external dependencies" section in
{{ link('user/getting_started.rst', 'Getting started') }} for more
information**

Flamingo supports interactive shells using ``flamingo shell`` for debugging.
If you bootstrapped your project according to
{{ link('user/getting_started.rst', 'Getting started') }} you can run
``make shell``.
