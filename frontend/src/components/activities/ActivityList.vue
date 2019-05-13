<template>

    <section class="activities">
        <h1>Aktiviteter</h1>
        <table>
            <thead>
                <tr>
                    <th>Aktivitet</th>
                    <th>Start</th>
                    <th>Slut</th>
                    <th>Navn</th>
                    <th>Økonomi</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <li v-for="a in acts" :key="a[0]">
                    <td><router-link :to="`/activity/${ a.pk }`">{{ a.activity }}</router-link></td>
                    <td>{{ new Date(a.startdate).toLocaleDateString() }}</td>
                    <td>{{ new Date(a.enddate).toLocaleDateString() }}</td>
                    <td>{{ a.payment.payee.name }}</td>
                    <td>{{ a.payment.total_amount }}</td>
                    <td>{{ a.status }}</td>
                </tr>
            </tbody>
        </table>
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
