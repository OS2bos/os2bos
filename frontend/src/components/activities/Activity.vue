<template>

    <section class="activity" v-if="act">
        <header class="activity-header">
            <h1>
                <i class="material-icons">style</i>
                Udgift til {{ activityId2name(act.service) }}
            </h1>
            <button @click="show_edit = !show_edit" class="act-edit-btn">Redigér</button>
        </header>

        <div v-if="show_edit">
            <activity-edit :activity-obj="act" v-if="show_edit" @save="reload()" />
        </div>

        <div class="activity-info" v-if="!show_edit">
            <dl>
                <dt>Status</dt>
                <dd>
                    <div v-html="statusLabel(act.status)"></div>
                </dd>
                <dt>
                    Type
                </dt>
                <dd>
                    <div v-if="act.activity_type === 'MAIN_ACTIVITY'">Foranstaltningsudgift</div>
                    <div v-if="act.activity_type === 'SUPPL_ACTIVITY'">Følgeudgift</div>
                </dd>
                <dt>Bevilges efter §</dt>
                <dd v-if="appr">{{ displaySection(appr.section) }}</dd>
                <dt>Aktivitet</dt>
                <dd>{{ activityId2name(act.service) }}</dd>
                <dt>Startdato</dt>
                <dd>{{ displayDate(act.start_date) }}</dd>
                <dt>Slutdato</dt>
                <dd>{{ displayDate(act.end_date) }}</dd>
                <dt>Bemærkning</dt>
                <dd>{{ act.note }}</dd>
            </dl>
            <dl>
                <h3>Beløb</h3>
                <dt>Afregningsenhed</dt>
                <dd>ikke implementeret</dd>
                <dt>Beløb</dt>
                <dd>ikke implementeret</dd>
            </dl>
            <dl>
                <h3>Betales til</h3>
                <dt>Betalingsmodtager</dt>
                <dd>ikke implementeret</dd>
                <dt>ID</dt>
                <dd>ikke implementeret</dd>
                <dt>Navn</dt>
                <dd>ikke implementeret</dd>
            </dl>
            <dl>
                <h3>Betaling</h3>
                <dt>Betalingsmåde</dt>
                <dd>ikke implementeret</dd>
            </dl>
        </div>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import ActivityEdit from './ActivityEdit.vue'
    import { json2js } from '../filters/Date.js'
    import { activityId2name, sectionId2name, displayStatus } from '../filters/Labels.js'

    export default {

        components: {
            ActivityEdit
        },
        data: function() {
            return {
                act: null,
                appr: null,
                cas: null,
                show_edit: false
            }
        },
        methods: {
            fetch_act: function(id) {
                axios.get(`/activities/${ id }`)
                .then(res => {
                    this.act = res.data
                    axios.get(`/appropriations/${ this.act.appropriation }`)
                    .then(resp => {
                        this.appr = resp.data
                        axios.get(`/cases/${ this.appr.case }`)
                        .then(response => {
                            this.cas = response.data
                            this.$store.commit('setBreadcrumb', [
                                {
                                    link: '/',
                                    title: 'Mine sager'
                                },
                                {
                                    link: `/case/${ this.cas.id }`,
                                    title: `Hovedsag ${ this.cas.sbsys_id }`
                                },
                                {
                                    link: `/appropriation/${ this.appr.id }`,
                                    title: `Foranstaltning ${ this.appr.sbsys_id }`
                                },
                                {
                                    link: false,
                                    title: `Udgift til ${ activityId2name(this.act.service) }`
                                }
                            ])
                        })
                    })
                })
                .catch(err => console.log(err))
            },
            reload: function() {
                this.show_edit =  false
            },
            displayDate: function(dt) {
                return json2js(dt)
            },
            activityId2name: function(id) {
                return activityId2name(id)
            },
            displaySection: function(id) {
                return sectionId2name(id)
            },
            statusLabel: function(status) {
                return displayStatus(status)
            }
        },
        created: function() {
            this.fetch_act(this.$route.params.id)
        }
    }
    
</script>

<style>

    .activity {
        margin: 1rem;
    }

    .activity-header {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
        justify-content: flex-start;
    }

    .activity .act-edit-btn {
        margin: 0 1rem;
    }

    .activity-info {
        display: grid; 
        grid-template-columns: auto auto auto auto;
        grid-gap: 3rem;
        justify-content: start;
        background-color: var(--grey1);
        padding: 1.5rem 2rem 2rem;
    }

</style>
