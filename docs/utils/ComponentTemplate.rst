.. {{ cls.__name__ }}:

-------------------------------
{{ cls.title }}
-------------------------------

{{ cls.tooltip }}

Categories:
    {{ ", ".join(cls.categories) }}
Works in:
    {{ ", ".join(cls.targets) }}

Parameters
-------------------------------
{% for categ in params %}
{{ categ }}
===============================

{{ categs[categ] }}

{% for param in params[categ] %}
.. {{ param.ref }}:
{{ param.label }}
    {{ param.hint }}
    {% if param.allowedLabels %}
    Options:
    {% for choice in param.allowedLabels %}
    * {{ choice }}
    {% endfor %}{% endif%}{% endfor %}{% endfor %}