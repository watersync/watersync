# URL architecture

## UI

Initially, I designed url architecture to quite strictly follow required connections between the data. So for example inside a project, there was fieldwork, then inside fieldwork there was location visit, then inside there was a measurement, which resulted in long urls: /projects/<project_pk>/fieldworks/<fieldwork_pk>/locationvisits/<locationvisit_pk>/measurements/<measurement_pk>.

In the second generation, I decided to flatten this and drop this long url pattern which was hard to manage automatically. Now practically all model data is accessible under e.g., /projects/<project_pk>/fieldworks, /projects/<project_pk>/gwl, /projects/<project_pk>/deployments. Whenever the list views are used outside of their "home page", `hx-vals` are used to generate url parameters that are passed with the request and the queryset is adjusted to provide only those items that are linked to the parent item.