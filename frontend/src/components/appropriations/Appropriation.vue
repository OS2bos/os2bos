<template>

    <section class="appropriation" v-if="appr">
        <header class="appropriation-header">
            <h1>
                <i class="material-icons">folder_open</i>
                Bevillingsskrivelse
            </h1>
            <div>
                <button v-if="!show_edit" @click="show_edit = true" class="appr-edit-btn">Redigér</button>
                <router-link :to="`/appropriation/${ appr.pk }/print`">Print</router-link>
            </div>
        </header>

        <div class="appr-grid">

            <div class="sagsbeh appr-grid-box">
                <dl>
                    <dt>Foranstaltningssag (SBSYS)</dt>
                    <dd>{{ appr.sbsys_id}}</dd>
                    <dt>Sagsbehandler</dt>
                    <dd>{{ appr.case.case_worker}} ({{ appr.case.case_worker_initials }})</dd>
                </dl>
            </div>

            <div class="sagspart appr-grid-box">
                <dl>
                    <dt>Sagspart</dt>
                    <dd>{{ appr.case.cpr_no }}, {{ appr.case.name }}</dd>
                    <dt>Betalingskommune</dt>
                    <dd>{{ appr.case.municipality_payment}}</dd>
                    <dt>Handlekommune</dt>
                    <dd>{{ appr.case.municipality_action}}</dd>
                    <dt>Bopælskommune</dt>
                    <dd>{{ appr.case.municipality_residence}}</dd>
                </dl>
            </div>
            
            <div class="sagslaw appr-grid-box">
                <dl> 
                    <dt>Bevilges efter §</dt>
                    <dd>{{ appr.law_ref }}</dd>
                </dl>
            </div>

            <div class="sagsbev appr-grid-box">
                <h2>Der bevilges:</h2>
                <activity-list :appr-id="appr.pk" />
            </div>
            
            <div class="sagsgodkend appr-grid-box">
                <span :class="`status-${ appr.status }`">{{ appr.status }}</span>
                <template v-if="appr.approval"> af
                    {{ appr.approval.approval_auth_level }} 
                    - {{ new Date(appr.approval.approval_date).toLocaleDateString() }}
                </template>
            </div>

        </div>

        <div class="appr-header">
            <div>
                
                <div v-if="show_edit">
                    <appropriation-edit :appropriation-data="appr" @cancelled="show_edit = false" @saved="show_edit = false" />
                </div>
            </div>
            <div>
                
            </div>
        </div>
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
                            title: `Foranstaltning ${ this.appr.sbsys_id }`
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

    .appr-grid {
        display: grid;
        grid-template-columns: repeat(6, auto);
        grid-template-rows: repeat(4, auto);
    }

    .appr-grid-box {
        border: solid 1px var(--grey1);
        padding: .5rem 1rem;
        margin: 1px;
    }

    .sagsbeh {
        grid-area: 1 / 1 / 2 / 4;
    }

    .sagspart {
        grid-area: 1 / 4 / 2 / 7;
    }

    .sagslaw {
        grid-area: 2 / 1 / 3 / 7;
    }

    .sagsbev {
        grid-area: 3 / 1 / 4 / 7;
    }


    .sagsgodkend {
        grid-area: 4 / 1 / 5 / 7;
    }

    @media screen and (min-width: 45rem) {
        
        .appropriation .appr-header {
            display: grid;
            grid-gap: 0 2rem;
            grid-template-columns: 1fr 1fr;
        }

    }

</style>
