<template>
    <article class="summary" v-if="appr">

        <h1>Bevillingsskrivelse - SBSYS ref. {{ appr.sbsys_id}}</h1>
    
        <dl>
            <dt>SBSYS-hovedsag</dt>
            <dd>{{ appr.case.sbsys_id}}</dd>
            <dt>Sagspart</dt>
            <dd>{{ appr.case.name }}, {{ appr.case.cpr_no }}</dd>
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
            <dt>Sagsbehandler</dt>
            <dd>{{ appr.case.case_worker}} ({{ appr.case.case_worker_initials }})</dd>
            <dt>Betalingskommune</dt>
            <dd>{{ appr.case.municipality_payment}}</dd>
            <dt>Handlekommune</dt>
            <dd>{{ appr.case.municipality_action}}</dd>
            <dt>Bopælskommune</dt>
            <dd>{{ appr.case.municipality_residence}}</dd>
        </dl>

    </article>
</template>

<script>

    import axios from '../http/Http.js'

    export default {

        data: function() {
            return {
                appr: null
            }
        },
        methods: {
            fetchAppr: function(id) {
                axios
                .get('../../appropriation-data.json')
                .then(res => {
                    this.appr = res.data
                })
                .catch(err => console.log(err))
            }
        },
        created: function() {
            this.fetchAppr(this.$route.params.id)
        }
    }
    
</script>

<style>

    .summary {
        margin: 2rem;
    }

    .summary .status-bevilget {
        background-color: var(--success);
        color: white;
        padding: .25rem;
    }

</style>