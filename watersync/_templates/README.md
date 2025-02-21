# Template logic

In the core template (_templates) directory there are highest-level layout templates that are used by all apps. Those templates define the layout of all pages.

* *base.html* - top-level template, contains global layout elements and loads packages.
* *base_.html* - templates with base_ prefix define layouts with navbars and sidebars. There are three separate templates. One for the landing page with the top navbar and two for the dashboard differing by the navigation options in the sidebar.
* *confirm_delete.html* - shared delete confirmation template
* e.g., *403.html* - error templates

Throughout Watersync we use HTMX for loading partial templates with data. This forces a particular structure of this directory and naming of files within. To begin with, each app has a directory. In that directory there are high-level layout templates and partial templates subdirectory.

## Layout templates

The main layout templates are essentially pages that are routed to the content section of each *base_.html* template. They will start with the breadcrumbs block followed by the actual content of the layout. They will include one or more partial templates to be rendered inside.

## Partial templates

Partial templates are supposed to be rendered in the context of a layout. They should not include (inherit) any of the base templates. There are two basic types of components used here: lists and detail panels.

### Detail panels

These are relevant for models that either have a lot of additional metadata that does not fit in a table or should collect additional information. For example, the Location model has a detail view and template that is basically a separate page, whereas sensor detail view and template are displayed in off-canvas panel.

### Tables & lists

The content of the tables is controlled at the list view set. Then, the table creation can be automated, because there is no need to manually control the columns anymore.

### Lists
