<template>

    <section class="appropriations">
        <h1>Bevillinger</h1>
        <ul class="list">
            <li v-for="a in apprs">
                <router-link :to="`/appropriation/${ a.pk }`">
                    {{ a.sbsys_id }} 
                </router-link>
                <span class="status">{{ a.status }}</span>
            </li>
        </ul>
    </section>

</template>

<script>

    import axios from '../http/Http.js'

    export default {

        props: [
            'caseId'
        ],
        data: function() {
            return {
                apprs: null   
            }
        },
        methods: {
            fetchAppropriations: function(case_id) {
                console.log(case_id)
                axios.get('../../appropriation-list-data.json')
                .then(res => {
                    this.apprs = res.data
                })
                .catch(err => console.log(err))
            }
        },
        created: function() {
            this.fetchAppropriations()
        }
    }
    
</script>

<style>

    .appropriations {
        margin: 1rem;
    }

    .appropriations .status {
        font-weight: bold;
        color: black;
    }

</style>
