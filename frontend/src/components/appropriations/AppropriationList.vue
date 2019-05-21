<template>

    <section class="appropriations">
        <header class="appropriations-header">
            <h1>Bevillinger</h1>
            <button class="appropriation-create-btn" @click="createAppr()">+ Ny bevilling</button>
        </header>
        <table>
            <thead>
            <tr>
                <th>Sags-ID</th>
                <th>Foranstaltningsudgift</th>
                <th>Aktivitet</th>
                <th>Følgeudgift</th>
                <th>Økonomi</th>
                <th>Status</th>
            </tr>
            </thead>
            <tbody>
                <tr v-for="a in apprs" :key="a[0]">
                    <td>    
                        <router-link :to="`/appropriation/${ a.pk }`">
                            {{ a.sbsys_id }} 
                        </router-link>
                    </td>
                    <td>{{ a.activities.main_law_ref }}</td>
                    <td>{{ a.activities.main_activity_name }}</td>
                    <td>{{ a.activities.activities_count }}</td>
                    <td>{{ a.payment.total_amount }}</td>
                    <td><span class="status">{{ a.status }}</span></td>
                </tr>
            </tbody>
        </table>
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
                axios.get('../../appropriation-list-data.json')
                .then(res => {
                    this.apprs = res.data
                })
                .catch(err => console.log(err))
            },
            createAppr: function() {
                axios.post('/') // POST new empty appropriation
                .then(res => {
                    this.$router.push(`/appropriation/${ res.data.pk }`) // Navigate to new appropriation page
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

    .appropriations-header {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
        justify-content: flex-start;
    }

    .appropriation-create-btn {
        margin: 0 1rem;
    }

    .appropriations .status {
        font-weight: bold;
        color: black;
    }

</style>
