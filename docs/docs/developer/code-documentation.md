# Docstrings

All docstrings are written in Google format. They document the intentions behind the code for other developers looking at Python files and are converted to reference documentation using mkdocs docstrings extension. Therefore, keeping them clean and tidy is critical.

## Model docstrings
Model docstrings are particularily important and must strictly adhere to the Google formatting. In the views, they are parsed using doctring-parser package and are converted to tooltips for users of the UI, explaining what each of the objects being stored by Watersync represent. 


"""Short description.

A bit more verbose description of what the element exactly is. For example give more details about the fieldwork variables or how the user should fill the fields. This can be as lenghty as necessary.

If you have something more to say about the code itself which is relevant only for the development, add the third block after two newlines. This part is not parsed.

Attributes:
Normal rest of the docstring. This part is also not parsed.
"""

## Views, Forms, Mixins, etc
Docstrings of other objects are not used in the UI. However, it is important to keep those precise and targeted. If you contribute a mixin or change something in a view, please make sure to update the docs according to the Google format.

# User guide
The user guid should only explain how to navigate the UI, highlight consequences of some actions, and explain the most common bugs that we are aware of. FAQ could also be used to explain the bugs.