==========================
Features and customization
==========================

The django-analytical application sets up basic tracking without any
further configuration.  This page describes extra features and ways in
which behavior can be customized.


.. _internal-ips:

Internal IP addresses
=====================

Visits by the website developers or internal users are usually not
interesting.  The django-analytical will comment out the service
initialization code if the client IP address is detected as one from the
:data:`ANALYTICAL_INTERNAL_IPS` setting.  The default value for this
setting is :data:`INTERNAL_IPS`.

Example:

.. code-block:: python

    ANALYTICAL_INTERNAL_IPS = ['192.168.1.45', '192.168.1.57']

.. note::

    The template tags can only access the visitor IP address if the
    HTTP request is present in the template context as the
    ``request`` variable.  For this reason, the
    :data:`ANALYTICAL_INTERNAL_IPS` setting only works if you add this
    variable to the context yourself when you render the template, or
    you use the ``RequestContext`` and add
    ``'django.core.context_processors.request'`` to the list of
    context processors in the ``TEMPLATE_CONTEXT_PROCESSORS``
    setting.


.. _identifying-visitors:

Identifying authenticated users
===============================

Some analytics services can track individual users.  If the visitor is
logged in through the standard Django authentication system and the
current user is accessible in the template context, the username can be
passed to the analytics services that support identifying users.  This
feature is configured by the :data:`ANALYTICAL_AUTO_IDENTIFY` setting
and is enabled by default.  To disable:

.. code-block:: python

    ANALYTICAL_AUTO_IDENTIFY = False

.. note::

    The template tags can only access the visitor username if the
    Django user is present in the template context either as the
    ``user`` variable, or as an attribute on the HTTP request in the
    ``request`` variable.  Use a
    :class:`~django.template.RequestContext` to render your
    templates and add
    ``'django.contrib.auth.context_processors.auth'`` or
    ``'django.core.context_processors.request'`` to the list of
    context processors in the :data:`TEMPLATE_CONTEXT_PROCESSORS`
    setting.  (The first of these is added by default.)
    Alternatively, add one of the variables to the context yourself
    when you render the template.

Changing the identity
*********************

If you want to override the identity of the logged-in user that the various
providers send you can do it by setting the ``analytical_identity`` context
variable in your view code:

.. code-block:: python

    context = RequestContext({'analytical_identity': user.uuid})
    return some_template.render(context)

or in the template:

.. code-block:: django

    {% with analytical_identity=request.user.uuid|default:None %}
        {% analytical_head_top %}
    {% endwith %}

or by implementing a context processor, e.g.

.. code-block:: python

    # FILE: myproject/context_processors.py
    from django.conf import settings

    def get_identity(request):
        return {
            'analytical_identity': 'some-value-here',
        }

    # FILE: myproject/settings.py
    TEMPLATES = [
        {
            'OPTIONS': {
                'context_processors': [
                    'myproject.context_processors.get_identity',
                ],
            },
        },
    ]

That allows you as a developer to leave your view code untouched and
make sure that the variable is injected for all templates.

If you want to change the identity only for specific provider use the
``*_identity`` context variable, where the ``*`` prefix is the module name
of the specific provider.
