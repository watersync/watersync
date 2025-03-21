# Forms

There is a single html template for all forms. All forms are passed to the template via htmx and are rendered in a modal. Form classes control the details of the form behaviour. For example, if you want the date to have a date picker, you should adjust this in the form by explicitly setting the date attribute to DateField and choose DateInput as widget.

Forms are rendered with django-crispy-forms.

Maps are handled separately and this is described in a separate page.