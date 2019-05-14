<template>

    <section class="appropriations">
        <h1>Bevillinger</h1>
        <table>
            <thead>
            <tr>
                <th>Sags-ID</th>
                <th>Hovedaktivitet</th>
                <th>Aktivitet</th>
                <th>Følgeudgift</th>
                <th>Øknomi</th>
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
                console.log(case_id)
                axios.get('../../appropriation-list-data.json')
                .then(res => {
                    this.apprs = res.data

                    /*

                    {
        "pk": 15,
        "case": {
            "pk": 2
        },
        "sbsys_id": "27.27.27-GX-9999-17-leil-20",
        "activities": {
            "main_law_ref": "§45 Ledsagerordning",
            "main_activity_name": "Ledsager",
            "activities_count": 3
        },
        "status": "forventet",
        "payment": {
            "total_amount": 25000
        }
    }

                    */
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
