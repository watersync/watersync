# URL architecture

## UI

In the newest generation, the URL patterns are flattened. Now practically all model data is accessible under e.g., /projects/<project_pk>/fieldworks, /projects/<project_pk>/gwl, /projects/<project_pk>/deployments. This enabled easy way to query all items related to the project. Then implementation of HTMX allows to query for items related to the particular location, fieldwork, etc., whenever necessary (mostly in overview pages).

## API

To be implemented.
