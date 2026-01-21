# Customized models

Generally the idea is to control as much of the appearance of the application as possible from the Python code. Models also play a role here. Some things to keep in mind when creating new models:

__## Relations__

* All relations should be named in a singular form (including m2m relationships).
* All related fields should have a `related_name` defined, which is the plural version of the related model name in lowercase letters.

__## str dunder method__

This method should be as simple as possible as it is used further down the line to represent the objects in verbose name.

__## Details__

If the model has a `JSONField`, it should be called `detail`, lowercase, singular. There is an automated way to display these in the `DetailView`s.

__## Description__

Some items may have just a simple comment attached to them (for example location visit) and some may need more text to understand the context (for example if something went wrong with sampling). All this should be added in a field called `description`. This way, that detail can be rendered either in a popover or in the detail page as a panel. This should be a `TextField`.

# ModelTemplateInterface

There is a mixin that defines some additional attributes for the Watersync models which are important in autmated list display. Among them are two dicionaries of model field names (keys) and their verbose representations (values):

* _list_view_fields - used to create table headers (list.html) and match them with the data to be displayed in the table (table.html).
* _detail_view_fields - used in the detail panel of objects (detail.html).

# SimpleHistorySetup

Some models (e.g., Location) use django-simple-history plugin which allowes to track changes to the objects and query the historical state of the database entry. There is a customization option for that plugin which allows to manually provide the date of modification of the object, allowing to alter the historical state. `SimpleHistorySetup` mixin has those additional fields and attributes defined.