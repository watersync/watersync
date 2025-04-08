# Detail template

Normally, when there is a template for displaying details of an object, there is a DetailView. Here we have WatersyncDetailView which handles most of the reusable logic.

## DetailContext

DetailContext is a mixin that helps to structure the context information for the DetailView.

## Reusable detail template

Take a look at the `detail.html` template. It's a reusable template that handles rendering of item details in a uniform way. There is a card with basic information, including toggable panel for json details, and a map, if item has geometry attribute.

base template is automatically determined depending on whether the detail is supposed to be rendered as a page, offcanvas or popover.

## Cusomizing the models

In order for the reusable template to work, new methods have to be created on the model that control which information is provided to the detail view. Also, each model should have a `__str__` method, because it is used as reference name of the object (for example as the page title).

## Details in forms
Initially JSONEditor was used to handle details of various objects. It has been changed to Django/HTMX implementation. Now, when the user presses the update or create button on an object, a check is made if the form contains a detail and type fields. If it does, then logic choosing an appropriate form is triggered. This assumes that the forms requireing details have a dictionary defined on them called detail_forms. That dictionary contains a mapping of options in the type field with appropriate form class.

Creation and updatind of the forms is handled in respective CreateView and UpdateView.