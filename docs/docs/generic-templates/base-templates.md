# Base templates

In Django templates you can reuse some of the html code by including partial templates (blocks of HTML code) with {% include %} tag or extending templates with {% extends %} tag. The latter is used mostly as layouts (higher level styling templates).

In Watersync codebase there are three base templates:

* base.html - main template which includes all meta elements, css and js imports and some globally elements like modals.
* base_landing.html - template handling the landing page, user registration login, etc. This template has a navbar on top and content at the bottom.
* base_dashboard.html - this template changes the layout to a dashboard layout with a sidebar on the left. Base dashboard is used for items that relevant at user level.
* project_dashboard.html - has the same structure as the base dashboard but manages items that are linked to project (hence change of navitems in the sidebar).
* blank.html - special template which only contains {% block content %}/{% endblock content %} tags. This was included to facilitate reusability of lists and detail templates as sole elements on the page and as blocks inside other templates (e.g., location overview). For some reason, when I included `extends base.html` block on top of it, thinking that it would help to load the relevant js and css code, it started breaking some elements like dropdowns. Without `bloc content` tag on the other hand nothing was displayed.