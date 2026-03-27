

Welcome to flamingo!
====================


Flamingo is a python3-based, pelican-inspired static site generator, made by
`Pengutronix <https://www.pengutronix.de>`__

Websites powered by flamingo:
 - `pengutronix.de <https://www.pengutronix.de>`__
 - `linux-automation.com <https://www.linux-automation.com/de/>`__


What is a static site generator?
--------------------------------

The most CMS based websites work by building every page on-demand with its
content fetched from a database and ran through a templating engine.

This makes totally sense if your content changes very frequently, but most
websites, blogs or documentation pages only change occasionally by manual
publishing.

Therefore rebuilding on every click is a unnecessary overhead, not only in
website performance but maintenance too.

A static site generator pre generates all pages of your website once to plain
HTML and CSS, which can be served by a simple webserver without any active
backend. This limits the complexity of your website to bare minimum and adds
security and reliability.


History of flamingo
-------------------

Why did we even bother writing a new static site generator from scratch?
Actually we didn't. 

In 2017 we redesigned our website `www.pengutronix.de <www.pengutronix.de>`__
with pelican. Our requirements and workflows are very specific and were hard to
met with existing pelican tools, so we developed a whole zoo of pelican plugins
and hacks, including a first, primitive version of a
{{ link('user/live_server.rst', 'Live-Server') }}, a custom blogging
engine and whole new reStructuredText sub system, over time.

In the end we had reinvented all aspects of pelican that were interesting for
us, but still had the pelican dependency to maintain.

So we threw all code we had in a new project and called it flamingo
(because flamingos are like fancy pelicans or something like that).

Flamingo started as a pelican drop-in replacement, but now it is a new,
from ground up re-designed static site generator.


Goal of flamingo
----------------

Flamingo is no specialized blogging engine or documentation tool, it is a
general solution for generating websites from markup languages. Basically it's
a fancy converter that takes rst, markdown, yaml or html and generates all
kinds of websites you can think of.


Target audience
---------------

Flamingo is no full featured content management system like WordPress for
instance. It has no built-in editor, user management or backup solution.

If you want to use flamingo you should be familiar with unix command lines and
using a text editor like vim, emacs, nano or eclipse.

If you want to develop plugins you need a basic understanding of python and
knowledge of `jinja2 <https://jinja.palletsprojects.com/>`__, HTML and CSS will
be useful.


Performance
-----------

Per definition, content managed with a static site generator gets written
rarely but read often.

This means long build times of multiple seconds or even up to minutes are
totally acceptable. Flamingo is designed to be easy and reusable, not to be
fast! It is written in pure python and all operations run in RAM.


Getting help
------------

If you have problems or suggestions, don't hesitate to ask for help!

Issue tracker: [`link <http://www.github.com/pengutronix/flamingo/issues>`__]

Email: [`entwicklung@pengutronix.de <entwicklung@pengutronix.de>`__]

Send patches: [`link <http://www.github.com/pengutronix/flamingo/>`__]
