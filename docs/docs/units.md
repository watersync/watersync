# Units

We implemented Pint in Watersync. This means that handling of the units is now more standardize. Instead of two fields on the Measurement model there is now one field taking a serialized representation of a Pint object. In the forms, user still has to pass both value and unit, which are further down combined into a string representation, validated and saved to the database in base units.
