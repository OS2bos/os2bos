<template>

    <section class="appropriation" v-if="appr">
        <header>
            <router-link :to="`/case/${ appr.case.pk }`"> Hovedsag {{ appr.case.sbsys_id }}</router-link>
            <dl>
                <dt>Sagspart CPR-nr</dt>
                <dd>{{ appr.case.cpr_no }}</dd>
                <dt>Sagspart navn</dt>
                <dd>{{ appr.case.name }}</dd>
                <dt>Sagsbehandler</dt>
                <dd>{{ appr.case.case_worker}} ({{ appr.case.case_worker_initials }})</dd>
            </dl>
            <dl>
                <dt>Betalingskommune</dt>
                <dd>{{ appr.case.municipality_payment}}</dd>
                <dt>Handlekommune</dt>
                <dd>{{ appr.case.municipality_action}}</dd>
                <dt>Bopælskommune</dt>
                <dd>{{ appr.case.municipality_residence}}</dd>
            </dl>
        </header>
        <h1>Bevillingsskrivelse</h1>
        <dl>
            <dt>SBSYS-sag</dt>
            <dd><strong>{{ appr.sbsys_id}}</strong></dd>
            <dt>Bevilling efter §</dt>
            <dd>{{ appr.law_ref }}</dd>
            <dt>Status</dt>
            <dd>
                <span :class="`status-${ appr.status }`">{{ appr.status }}</span>
                <template v-if="appr.approval">
                    af
                    {{ appr.approval.approval_person }}, 
                    {{ appr.approval.approval_auth_level }} 
                    - {{ new Date(appr.approval.approval_date).toLocaleDateString() }}
                </template>
            </dd>        
        </dl>
        <activity-list :appr-id="appr.pk" />
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import ActivityList from '../activities/ActivityList.vue'

    export default {

        components: {
            ActivityList
        },
        data: function() {
            return {
                appr: null
            }
        },
        methods: {
            fetch_appr: function(id) {
                axios
                .get('../../appropriation-data.json')
                .then(res => {
                    this.appr = res.data
                })
                .catch(err => console.log(err))
            }
        },
        created: function() {
            this.fetch_appr(this.$route.params.id)
        }
    }
    
</script>

<style>

    .appropriation {
        margin: 1rem;
    }

    .appropriation .status-bevilget {
        background-color: var(--success);
        color: white;
        padding: .25rem;
    }

</style>
