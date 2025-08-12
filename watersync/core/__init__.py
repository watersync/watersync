"""
## Core module

This module contains the core models and managers for the application that are
shared across different apps. It represents the main part of user's workflow
when working with the application.

User has a project -->
project has locations -->
user performs performs multiple fieldworks throughout the project -->
On each day, the user visits one or more locations (or none) -->
At each location, the user takes measurements.

### Project
The main object in the database. All other objects are connected to the project.
Depending on whether the user is attached to the project, the user can see the data
related to the project.

### Location
Location model contains the list of measurement points. They are attached to projects.

### Fieldwork
In projects, users will perform fieldwork. Fieldwork is an event when the user
visits the project location on a date and collects data. Within the fieldwork,
the user can visit one or more locations (points where measurements are taken). This
model contains top-level information about the fieldwork day.
"""
