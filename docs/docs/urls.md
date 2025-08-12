# URL architecture

## UI

In the newest generation, the URL patterns are flattened. Now practically all model data is accessible under e.g., /projects/<project_pk>/fieldworks, /projects/<project_pk>/gwl, /projects/<project_pk>/deployments. This enabled easy way to query all items related to the project. Then implementation of HTMX allows to query for items related to the particular location, fieldwork, etc., whenever necessary (mostly in overview pages).

## API

To be implemented.

## URL pattern standardization

URL patterns are specified in the urls.py files for transparency. They follow these conventions:

- Lists: `app_label:model_name_plural`, e.g., `sensors:sensors`
- Create: `app_label:add-model_name`, e.g., `sensors:add-sensor`
- Update: `app_label:update-model_name`, e.g., `sensors:update-sensor`
- Delete: `app_label:delete-model_name`, e.g., `sensors:delete-sensor`
- Detail: `app_label:detail-model_name`, e.g., `sensors:detail-sensor`

If the model is composed of several words (e.g., GWLMeasurement), both words are concatenated together in lowercase (no dashes, or underscores are added to the patterns.)

The models names are always in singular form (e.g., Location). In `watersync.core.generics.views.StandardURLMixin` we automate generation of those patterns for templates, which are passed thorugh `ListContext` object.

The tag representing the detail of a specific record is always `<model_name_pk>`. `model_name` is handled consistently with the rest of url pattenrns (i.e., plain concatenation, e.g., `gwlmeasurements` for lists and `gwlmeasurement` for other actions).
