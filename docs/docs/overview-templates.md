# Overview templates

Initially DetailView's of some models were used to render overviews of for example resources linked to the item. For example the LocationDetailView contained a lot of logic that was additionally querying other Views to get all measurements from that location. This had to be changed to provide more modular structure.

Now, detail are only responsible for rendering the datail panel of the item (for example the parameters of the piezometers). Any additional resources are handled by a separate view called LocationResourcesOverview. The naming convention is kept over other items too. These also have their own templates tha combine all the bits from the views they query. Perfectly modular design.