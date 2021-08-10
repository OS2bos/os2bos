# Dataflow in the application

The frontend GUI, unsurprisingly, presents data from the backend to the user. 
Data is fetched from the backend via REST API and fed to its various parts via a mix of component properties and application state (ie. [Vuex](https://vuex.vuejs.org/api/)).

This chapter describes these dataflows in detail.


## Dataflow when fetching and displaying information

**Note** that the below example describes an ideal dataflow and that the codebase might differ from it in its current state.

The frontend application goes through the following staps to display data to the user:

1. User navigates to a page and its corresponding _main component_ picks up the route parameters
2. _Main components_ use route params to fetch data via REST API
3. _Subcomponents_ are updated via props or state
4. Data is subsequently displayed to the user via Vue template bindings

Let's explore these steps in greater detail ...

### User navigates to page
User navigates to page and [Vue Router](https://router.vuejs.org/api/) updates the view and its parameters (`$route.params`).

### Compontent pick up route parameters
The route's _main component_ picks up the route parameters (ex. `route.params.actId`) at the _created_ lifecycle hook **and** at route update events like so:
```
created: function() {
    this.activity_id = this.$route.params.actId
},
beforeRouteUpdate(to, from, next) {
    this.activity_id = to.params.actId
    next()
}
```

### _main component_ uses route params to fetch data
The _main component_ uses route params to fetch data via REST API. 

**Using state:**
```
$state.dispatch('fetchActivity', this.activity_id)
```
and a corresponding _getter_:
```
computed: {
    activity_data: function() {
        return this.$state.getters.getActivity()
    }
}
```

**Not using state:** 
Fetching data directly using [axios](https://github.com/axios/axios) if no state update is needed:
```
axios.get(`/activity/${ this.activity_id }/`).then(response => {
    this.activity_data = response.data
})
```

### _Subcomponents_ are updated via props or state
_Subcomponents_ that are included in the main component may be passed the fetched data as a `prop` or get data from state.

**Using state:** 
If we can assume the main component has updated the state, fetch data from state using a _getter_:
```
computed: {
    activity_data: function() {
        return this.$state.getters.getActivity()
    }
}
```

**Not using state:** 
The component listens for changes to `props` in order to update its content:
```
props: [
    'activityData'    
],
data: function() {
    return {
        activity_data: this.activityData
    }
},
watch: {
    activityData: function(new_value, old_value) {
        this.activity_data = new_value
    }
}
```


## Dataflow when manipulating data

Here is another idealized dataflow for when users create or update data via the UI:

1. User changes a value in an input element
2. A `POST` or `PATCH` request is sent to REST API
3. REST API response updates state or current template

Let us explore these steps in greater detail ...

### User changes a value in an input element
Typically, a user will interact with an `<input>` element of some sort that is bound to a component's variables via `v-model` or via a method run on a `change` or `input` event.

### A POST or PATCH request is sent to REST API
User input can cause a method call to send a `POST`/`PATCH` request in different ways.

**By event**
```
<template>
    <input type="text" @input="inputUpdateHandler">
</template>

<script>
    ...
    methods: {
        inputUpdateHandler: function(ev) {
            axios.post('/endpoint/', ev.target.value)
        }
    }
    ...
</script>
```

**By value binding**
```
<template>
    <input type="text" v-model="input_value">
</template>

<script>
    ...
    watch: {
        input_value: function(new_value, old_value) {
            axios.post('/endpoint/', new_value)
        }
    }
    ...
</script>
```

### REST API response updates state or current template
When a REST API request is successful, it should update the state by mutation call (`commit`).
If no state applies, it should update the current component's properties.
