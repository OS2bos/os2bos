# Dataflow in the application

The frontend GUI, unsurprisingly, presents data from the backend to the user. 
Data is fetched from the backend via REST API and fed to its various parts via a mix of component properties and application state (ie. [Vuex](https://vuex.vuejs.org/api/)).

This chapter describes these dataflows in detail.


## Dataflow when fetching and displaying information

**Note** that the below example describes an ideal dataflow and that the codebase might differ from it in its current state.

1. User navigates to page and [Vue Router](https://router.vuejs.org/api/) updates the view and its parameters (`$route.params`).

2. The route's _main component_ picks up the route parameters (ex. `route.params.actId`) at the _created_ lifecycle hook **and** at route update events like so:
    ```
    created: function() {
        this.activity_id = this.$route.params.actId
    },
    beforeRouteUpdate(to, from, next) {
        this.activity_id = to.params.actId
        next()
    }
    ```

3. The _main component_ uses route params to fetch data via REST API. 
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

4. _Subcomponents_ that are included in the main component may be passed the fetched data as a `prop` or get data from state.
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
   
5. Data is subsequently displayed to the user via Vue template.
