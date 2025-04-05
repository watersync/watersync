# Docstrings

Good code has docstrings. Period. Great code has well written docstrings! If you are already there, why not use those docstrings within the application as well?

We reuse docstrings to display explanation about data in the templates. In the generics, the docstring is split into segments to obtain the relevant information. The first part which normally is a succinct description of the model becomes the main explanation. The second part, normally verbose, explaining what the class is doing in more datail becomes the detail explanation.

Parts are split be double newlines ("\n\n"). Therefore, it is necessary that the dosctring keep the right structure:

"""Short description.

A bit more verbose description of what the element exactly is. For example give more details about the fieldwork variables or how the user should fill the fields. This can be as lenghty as necessary.

If you have something more to say about the code itself which is relevant only for the development, add the third block after two newlines.

Attributes:
Normal rest of the docstring.
"""