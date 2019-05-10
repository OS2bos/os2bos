<template>

    <section class="activity" v-if="act">
        <router-link to="/appropriation/x">Bevilling YYY</router-link>
        <h1>Aktivitet {{ act.activity }}</h1>
        <dl>
            
        </dl>
    </section>

</template>

<script>

    import axios from '../http/Http.js'

    export default {

        data: function() {
            return {
                act: null
            }
        },
        methods: {
            update: function() {
                this.fetch_appr(this.$route.params.id)
            },
            fetch_appr: function(id) {
                axios.get('../../activity-1-data.json')
                .then(res => {
                    this.act = res.data
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

    .activity {
        margin: 1rem;
    }

</style>
