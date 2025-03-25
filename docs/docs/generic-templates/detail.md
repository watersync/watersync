# Detail template

Normally, when there is a template for displaying details of an object, there is a DetailView. Here we have WatersyncDetailView which handles most of the reusable logic.

## DetailContext

DetailContext is a mixin that helps to structure the context information for the DetailView.

## Reusable detail template

Take a look at the `detail.html` template. It's a reusable template that handles rendering of item details in a uniform way. There is a card with basic information, including toggable panel for json details, and a map, if item has geometry attribute.

base template is automatically determined depending on whether the detail is supposed to be rendered as a page, offcanvas or popover.

## Cusomizing the models

In order for the reusable template to work, new methods have to be created on the model that control which information is provided to the detail view. Also, each model should have a `__str__` method, because it is used as reference name of the object (for example as the page title).