# Generic templates

Generally the idea in Watersync codebase is to control as much of the appearance of the application as possible from the Python code. This led to a number of mixins, generic views, context processor, etc, that use the extra information from the models and the views for rendering the content.

As explained in the [code documentation](../code-documentation.md), model