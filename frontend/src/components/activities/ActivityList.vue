<template>

    <section class="activities">
        <button class="activities-create-btn" title="Ny aktivitet" @click="createAct()">+ Tilføj ydelse</button>
        <table>
            <thead>
                <tr>
                    <th>Ydelse</th>
                    <th>Start</th>
                    <th>Slut</th>
                    <th>Navn</th>
                    <th>Økonomi</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="a in acts" :key="a[0]">
                    <td><router-link :to="`/activity/${ a.pk }`">{{ a.activity }}</router-link></td>
                    <td>{{ new Date(a.startdate).toLocaleDateString() }}</td>
                    <td>{{ new Date(a.enddate).toLocaleDateString() }}</td>
                    <td>{{ a.payment.payee.name }}</td>
                    <td>{{ a.payment.total_amount }}</td>
                    <td>{{ a.status }}</td>
                </tr>
                <tr>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td>
                        {{ total_amounts}}
                    </td>
                    <td></td>
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
        computed: {
            total_amounts: function() {
                function getTotal(total, act) {
                    console.log(total)
                    console.log(act.payment.total_amount)
                    return total + act.payment.total_amount
                }
                if (this.acts) {
                    return this.acts.reduce(getTotal, 0)
                }
            }
        },
        methods: {
            fetchActivities: function(appropriation_id) {
                axios.get('../../activity-list-data.json')
                .then(res => {
                    this.acts = res.data
                })
                .catch(err => console.log(err))
            },
            createAct: function() {
                axios.post('/') // POST new empty activity
                .then(res => {
                    this.$router.push(`/activity/${ res.data.pk }`) // Navigate to new activity page
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

    .activities-header {
        display: flex;
        flex-flow: row nowrap;
        justify-content: flex-start;
        align-items: center;
    }

    .activities-create-btn {
        margin: 0 0 1rem;
    }

</style>
