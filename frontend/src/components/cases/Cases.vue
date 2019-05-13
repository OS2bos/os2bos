<template>

    <section class="cases" v-if="cas">
        <h1>Mine sager</h1>
        <ul class="list">
            <li>Sags-ID Navn Ændret</li>
            <li>
                <router-link to="/case/1">
                    {{ cas.sbsys_id }}
                </router-link>
                {{ cas.name }} {{ cas.updated }}
            </li>
            <li>
                <router-link to="/case/2">
                    {{ cas.sbsys_id }}
                </router-link>
                {{ cas.name }} {{ cas.updated }}
            </li>
            <li>
                <router-link to="/case/3">
                    {{ cas.sbsys_id }}
                </router-link>
                {{ cas.name }} {{ cas.updated }}
            </li>
        </ul>
    </section>

</template>

<script>

    import axios from '../http/Http.js'

    export default {

        data: function() {
            return {
                cas: null
            }
        },
        methods: {
            update: function() {
                this.fetch_case(this.$route.params.id)
            },
            fetch_case: function(id) {
                axios.get('../../case.json')
                .then(res => {
                    this.cas = res.data
                })
                .catch(err => console.log(err))
            }
        },
        created: function() {
            this.update()
        }
        
    }
    
</script>

<style>

    .cases {
        margin: 1rem;
    }

</style>
