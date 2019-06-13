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

        <div v-if="!show_edit">
            <dl>
                <dt>Status</dt>
                <dd>
                    <div v-html="statusLabel(act.status)"></div>
                </dd>
                <dt>Type</dt>
                <dd>
                    <div>{{ act.activity_type }}</div>
                </dd>
                <dt>Aktivitet</dt>
                <dd>{{ activityId2name(act.service) }}</dd>
                <dt>Startdato</dt>
                <dd>{{ displayDate(act.start_date) }}</dd>
                <dt>Slutdato</dt>
                <dd>{{ displayDate(act.end_date) }}</dd>
            </dl>
            <h2>Udgifter</h2>
            <dl>
                <dt>Beløb</dt>
                <dd>ikke implementeret</dd>
                <dt>Afregningsenhed</dt>
                <dd>
                    <template>
                        <p>Kroner pr. måned ikke implementeret</p>
                        <p>Første år ikke implementeret</p>
                        <p>Årligt ikke implementeret</p>
                    </template>
                    <template>
                        <p>Enkeltudgift ikke implementeret</p>
                    </template>
                </dd>
                <dt>Bemærkninger</dt>
                <dd>ikke implementeret</dd>
            </dl>
            <h3>Betalingsmodtager</h3>
            <dl>
                <dt>Type</dt>
                <dd>ikke implementeret</dd>
                <dt>ID</dt>
                <dd>ikke implementeret</dd>
                <dt>Navn</dt>
                <dd>ikke implementeret</dd>
                <dt>Betalingsmåde</dt>
                <dd>
                    <span>
                        ikke implementeret
                    </span>
                </dd>
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
                    this.$store.commit('setBreadcrumb', [
                        {
                            link: '/',
                            title: 'Mine sager'
                        },
                        {
                            link: `/appropriation/${ this.appr.id }`,
                            title: `Foranstaltning ${ this.appr.sbsys_id }`
                        },
                        {
                            link: false,
                            title: `${ activityId2name(this.act.service) }`
                        }
                    ])
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

</style>
