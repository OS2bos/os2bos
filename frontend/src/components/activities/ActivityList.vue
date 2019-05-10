<template>

    <section class="activities">
        <h1>Aktiviteter</h1>
        <ul class="list">
            <li v-for="a in acts">
                <router-link :to="`/activity/${ a.pk }`">{{ a.activity }}</router-link>
            </li>
        </ul>
    </section>

</template>

<script>

    import axios from '../http/Http.js'

    export default {

        props: [
            'apprId'
        ],
        data: function() {
            return {
                acts: null   
            }
        },
        methods: {
            fetchActivities: function(appropriation_id) {
                console.log(appropriation_id)
                axios.get('../../activity-list-data.json')
                .then(res => {
                    this.acts = res.data
                })
                .catch(err => console.log(err))
            }
        },
        created: function() {
            if (this.apprId) {
                this.fetchActivities(this.apprId)
            }
        }
    }
    
</script>

<style>

    .activities {
        margin: 1rem;
    }

</style>
