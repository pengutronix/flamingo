is_template: False


Data Model
==========

The data model is designed to behave similar to the
`Django <https://docs.djangoproject.com/en/2.2/topics/db/queries/>`_ ORM.
The examples may be simple but flamingo should be capable of nearly all Django
ORM operations that make sense to implement without SQL.

Examples
--------

.. code-block:: python

    # all following examples use a ContentSet 'cs' created like this:

    In [1]: from flamingo import ContentSet, Q

    In [2]: cs = ContentSet()

    In [3]: for i in range(5):
       ...:     cs.add(a=i)
       ...:

    In [4]: cs
    Out[4]: <ContentSet(<Content(a=0)>, <Content(a=1)>, <Content(a=2)>, <Content(a=3)>, <Content(a=4)>)>


Slices
``````

.. code-block:: python

    # get all contents from index 1 to index 3

    In [1]: cs[1:3]
    Out[1]: <ContentSet(<Content(a=1)>, <Content(a=2)>)>


Simple filtering and excluding
``````````````````````````````

.. code-block:: python

    # find all content objects with a == 2

    In [1]: cs.filter(a=2)
    Out[1]: <ContentSet(<Content(a=2)>)>

    # find all content objects with a != 2

    In [2]: cs.exclude(a=2)
    Out[2]: <ContentSet(<Content(a=0)>, <Content(a=1)>, <Content(a=3)>, <Content(a=4)>)>

    # get content object with a == 2

    In [3]: cs.get(a=2)
    Out[3]: <Content(a=2)>)


Filter chaining
```````````````

.. code-block:: python

    # find all content objects with a greater than 1 and a lower than 4

    In [1]: cs.filter(a__gt=1).filter(a__lt=4)
    Out[1]: <ContentSet(<Content(a=2)>, <Content(a=3)>)>


Filter by callback
``````````````````

.. code-block:: python

    # find all content objects with a modulo 3 is 0

    In [1]: cs.filter(a__passes=lambda a: a % 3 == 0)
    Out[1]: <ContentSet(<Content(a=0)>, <Content(a=3)>)>


Negated Filter
``````````````

.. code-block:: python

    # find all content objects with a is not 0

    In [1]: cs.filter(~Q(a=0))
    Out[1]: <ContentSet(<Content(a=1)>, <Content(a=2)>, <Content(a=3)>,
                        <Content(a=4)>)>


OR related Qs
`````````````

.. code-block:: python

    # find all content objects with a equal 2 or 4

    In [1]: cs.filter(Q(a=2) | Q(a=4))
    Out[1]: <ContentSet(<Content(a=2)>, <Content(a=4)>)>

Since ``|`` and ``~`` are reserved expressions in Jinja2,
``flamingo.core.data_model.OR``, ``flamingo.core.data_model.AND`` and 
``flamingo.core.data_model.NOT`` are used in templates:

.. code-block:: jinja

    {{ context.contents.filter( OR(Q(a=1), NOT(Q(a=2)) )) }}


Interleaved Qs
``````````````

.. code-block:: python

    # find all content objects with a equal (1, 2) or 3

    In [1]: cs.filter(Q(Q(a=1) | Q(a=2)) | Q(a=3))
    Out[1]: <ContentSet(<Content(a=1)>, <Content(a=2)>, <Content(a=3)>)>


F objects
`````````

.. code-block:: python

    # find all content objects with a equal b

    In [1]: from flamingo import ContentSet, Q, F

    In [2]: cs = ContentSet()

    In [3]: for i in range(5):
       ...:     cs.add(a=i, b=1)
       ...:

    In [4]: cs
    Out[4]: <ContentSet(<Content(a=0, b=1)>, <Content(a=1, b=1)>,
                        <Content(a=2, b=1)>, <Content(a=3, b=1)>,
                        <Content(a=4, b=1)>)>

    In [5]: cs.filter(a=F('b'))
    Out[5]: <ContentSet(<Content(a=1, b=1)>)>


Available Lookups
`````````````````

.. table::

    ^Name   ^Operation ^Description
    |eq  |== |A is equal B |
    |ne  |!= |A is unequal B |
    |lt  |<  |A is lower than B |
    |lte |<= |A is lower equal than B
    |gt  |>  |A is greater than B |
    |gte |>= |A is greater equal than B |
    |in  |in |A is in B |
    |isnull |is None |A is None |
    |isfalse |is False |A is False |
    |contains |str(A) in str(B) |A contains B as string, case sensitive |
    |icontains |str(A).lower() in str(B).lower() |A contains B as string, case insensitive |
    |startswith |str(A).startswith(str(B)) |A startswith B as string, case sensitive |
    |istartswith |str(A).lower().startswith(str(B).lower()) |A startswith B as string, case insensitive |
    |passes |B(A) |A passes B |


Content / ContentSet API
------------------------

Add Contents to ContentSets
```````````````````````````

.. code-block:: python

    # ContentSet.add() takes Content objects or keyword arguments to create
    # a Content object on the fly

    In [1]: from flamingo import ContentSet, Content

    In [2]: cs = ContentSet()
    Out[2]: <ContentSet()>

    In [3]: cs.add(Content(a=1))

    In [4]: cs.add(a=2)

    In [5]: cs
    In [5]: <ContentSet(<Content(a=1)>, <Content(a=2)>)>


First / Last
````````````

.. code-block:: python

    In [1]: from flamingo import ContentSet

    In [2]: cs = ContentSet()

    In [3]: for i in range(5):
       ...:     cs.add(a=i)
       ...:

    In [4]: cs
    Out[4]: <ContentSet(<Content(a=0)>, <Content(a=1)>, <Content(a=2)>, <Content(a=3)>, <Content(a=4)>)>

    In [5]: cs.first()
    Out[5]: <Content(a=0)>

    In [6]: cs.last()
    Out[6]: <Content(a=4)>


Count
`````

.. code-block:: python

    In [1]: from flamingo import ContentSet

    In [2]: cs = ContentSet()

    In [3]: cs.count()
    Out[3]: 0

    In [3]: len(cs)
    Out[3]: 0
