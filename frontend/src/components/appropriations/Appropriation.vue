<template>

    <section class="appropriation" v-if="appr">
        <header class="appropriation-header">
            <h1>Bevillingsskrivelse</h1>
            <button v-if="!show_edit" @click="show_edit = true" class="appr-edit-btn">Redigér</button>
        </header>
        <div class="appr-header">
            <div>
                <dl v-if="!show_edit">
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
                <div v-if="show_edit">
                    <appropriation-edit :appropriation-data="appr" @cancelled="show_edit = false" @saved="show_edit = false" />
                </div>
            </div>
            <div>
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
            </div>
        </div>
        <activity-list :appr-id="appr.pk" />
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import ActivityList from '../activities/ActivityList.vue'
    import AppropriationEdit from './AppropriationEdit.vue'

    export default {

        components: {
            ActivityList,
            AppropriationEdit
        },
        data: function() {
            return {
                appr: null,
                show_edit: false
            }
        },
        methods: {
            fetchAppr: function(id) {
                axios
                .get('../../appropriation-data.json')
                .then(res => {
                    this.appr = res.data
                    this.$store.commit('setBreadcrumb', [
                        {
                            link: '/',
                            title: 'Mine sager'
                        },
                        {
                            link: `/case/${ this.appr.case.pk }`,
                            title: `Sag ${ this.appr.case.sbsys_id }`
                        },
                        {
                            link: false,
                            title: `Bevilling ${ this.appr.sbsys_id }`
                        }
                    ])
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

    .appropriation {
        margin: 1rem;
    }

    .appropriation-header {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
        justify-content: flex-start;
    }

    .appropriation .appr-edit-btn {
        margin: 0 1rem;
    }

    .appropriation .status-bevilget {
        background-color: var(--success);
        color: white;
        padding: .25rem;
    }

    @media screen and (min-width: 45rem) {
        
        .appropriation .appr-header {
            display: grid;
            grid-gap: 0 2rem;
            grid-template-columns: 1fr 1fr;
        }

    }

</style>
