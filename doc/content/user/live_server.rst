

Live-Server
===========

The Live-Server is one of the core features of flamingo, and contains all sorts
tools for debugging and content creation.

**The flamingo Live-Server is only meant for development, not for deployment!**


Basic usage
-----------

If you bootstrapped your project like described in
{{ link('user/getting_started.rst', 'getting started') }}, you can start
a Live-Server by running ``make server``, then open up ``localhost:8080``
in your favorite web browser.

You can change the port of the webserver like this:
``make server args="--port=8081"``.

The browser tab is meant to leave open while you write content. The server
will recognize changes in ``settings.CONTENT_ROOT`` and will rebuild and
refresh automatically.

.. img:: screenshot-1.png
    :width: 400px

The black bar on top is a debug toolbar. If you click on "Flamingo" or hit
[ESC] on your keyboard, a panel drops down. This panel holds meta data of the
currently shown page.

.. img:: screenshot-2.png
    :width: 400px

If you restart the Live-Server, the browser tab will recognize the disconnect
and wait for the server to restart.

.. img:: reconnecting.png
    :width: 400px

If your project produces warnings the debug toolbar will display a pulsing
warning counter. On click it will display details off the warning.

The shown warning was produced by making a title underline in a rst file to
short.

.. img:: warning-closed.png
    :width: 400px

.. img:: warning-open.png
    :width: 400px

When an error occurs flamingo will to try to pretty print them.

This error was produced by using a unknown rst directive.

.. img:: error-closed.png
    :width: 400px

.. img:: error-open.png
    :width: 400px

When an error occurs flamingo can't pretty print, it will pretty print the
underlying stack trace.

.. img:: stack-trace.png
    :width: 400px


Shell
-----

When you open the debug bar, and hit the button ``Start Shell`` the server
will start an IPython console. This console does essential the same as
``make shell`` but can run aside the webserver.

The shell has access to the ``context`` and all ``contents``.

.. code-block:: text

    In [1]: context
    Out[1]: <flamingo.core.context.Context at 0x7f8ab65ec7f0>

    # this will start an editor with the corresponding content file in it
    In [2]: context.contents.last().edit()

    # this 
    In [2]: context.contents.last().edit()
