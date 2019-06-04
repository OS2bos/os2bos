<template>

    <section class="appropriation" v-if="appr">
        <header class="appropriation-header">
            <h1>Bevillingsskrivelse</h1>
            <div>
                <button @click="show_edit = !show_edit" class="appr-edit-btn">Redigér</button>
                <router-link :to="`/appropriation/${ appr.id }/print`">Print</router-link>
            </div>
        </header>

        <div v-if="show_edit">
            <appropriation-edit :appr-obj="appr" v-if="show_edit" @close="update()" />
        </div>

        <div class="appr-grid" v-if="cas">

        <template v-if="!show_edit">
            <div class="sagsbeh appr-grid-box">
                <dl>
                    <dt>Foranstaltningssag (SBSYS)</dt>
                    <dd>{{ appr.sbsys_id}}</dd>
                    <dt>Sagsbehandler</dt>
                    <dd>{{ cas.case_worker}}</dd>
                </dl>
            </div>

            <div class="sagspart appr-grid-box">
                <dl>
                    <dt>Sagspart</dt>
                    <dd>{{ cas.cpr_number }}, {{ cas.name }}</dd>
                    <dt>Betalingskommune</dt>
                    <dd>{{ cas.paying_municipality }}</dd>
                    <dt>Handlekommune</dt>
                    <dd>{{ cas.acting_municipality }}</dd>
                    <dt>Bopælskommune</dt>
                    <dd>{{ cas.residence_municipality }}</dd>
                </dl>
            </div>
            
            <div class="sagslaw appr-grid-box">
                <dl> 
                    <dt>Bevilges efter §</dt>
                    <dd>{{ displaySection(appr.section) }}</dd>
                </dl>
            </div>
        </template>

            <div class="sagsbev appr-grid-box">
                <h2>Der bevilges:</h2>
                <!-- <activity-list :appr-id="appr.id" /> -->
                <!-- <activity-list2 :appr-id="appr.id" /> -->
                <activity-list3 :appr-id="appr.id" />
                <!-- <activity-list4 :appr-id="appr.id" /> -->
            </div>
            
            <div class="sagsgodkend appr-grid-box">
                <span :class="`status-${ appr.status }`">{{ appr.status }}</span>
                <template v-if="appr.approval_level"> af
                    {{ appr.approval_level }}
                </template>
            </div>

        </div>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import ActivityList from '../activities/ActivityList.vue'
    import ActivityList2 from '../activities/ActivityList2.vue'
    import ActivityList3 from '../activities/ActivityList3.vue'
    import ActivityList4 from '../activities/ActivityList4.vue'
    import AppropriationEdit from './AppropriationEdit.vue'
    import { sectionId2name } from '../filters/Labels.js'

    export default {

        components: {
            ActivityList,
            ActivityList2,
            ActivityList3,
            ActivityList4,
            AppropriationEdit
        },
        data: function() {
            return {
                appr: null,
                cas: null,
                show_edit: false
            }
        },
        methods: {
            update: function() {
                this.show_edit =  false
                this.fetchAppr(this.$route.params.id)
            },
            displaySection: function(id) {
                return sectionId2name(id)
            },
            fetchAppr: function(id) {
                axios.get(`/appropriations/${ id }`)
                .then(res => {
                    this.appr = res.data

                    axios.get(`/cases/${ res.data.case }`)
                    .then(resp => {
                        this.cas = resp.data
                        this.$store.commit('setBreadcrumb', [
                            {
                                link: '/',
                                title: 'Mine sager'
                            },
                            {
                                link: `/case/${ this.appr.case }`,
                                title: `${ this.cas.sbsys_id }, ${ this.cas.name }`
                            },
                            {
                                link: false,
                                title: `Foranstaltning ${ this.appr.sbsys_id }`
                            }
                        ])

                    })
                })
                .catch(err => console.log(err))
            }
        },
        created: function() {
            this.update()
        }
    }
    
</script>

<style>

    .appropriation {
        margin: 0 1rem 1rem;
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

    .appropriation .status-Godkendt {
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
