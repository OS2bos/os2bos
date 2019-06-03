<template>

    <section class="activity" v-if="act">
        <header class="activity-header">
            <h1>
                <i class="material-icons">style</i>
                Udgift til {{ act.activity_type }}
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
                    <div :class="`status-${ act.status }`">{{ act.status }}</div>
                </dd>
                <dt>Type</dt>
                <dd>
                    <div v-if="act.is_main_act">Hovedaktivitet</div>
                    <div v-if="!act.is_main_act">Tillægsydelse</div>
                    <div v-if="act.is_single_payment">Enkeltudgift</div>
                    <div v-if="!act.is_single_payment">Følgeydelse</div>
                </dd>
                <dt>Bevilling efter </dt>
                <dd>ikke implementeret</dd>
                <dt>Aktivitet</dt>
                <dd>{{ act.activity_type }}</dd>
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
                <dd>{{ act.user_created }}</dd>
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

    export default {

        components: {
            ActivityEdit
        },
        data: function() {
            return {
                act: null,
                show_edit: false
            }
        },
        methods: {
            fetch_act: function(id) {
                axios.get(`/activities/${ id }`)
                .then(res => {
                    this.act = res.data
                    this.$store.commit('setBreadcrumb', [
                        {
                            link: '/',
                            title: 'Mine sager'
                        },
                        // {
                        //     link: `/case/${ this.act.appropriation.case.id }`,
                        //     title: `${ this.act.appropriation.case.sbsys_id }, ${ this.act.appropriation.case.name }`
                        // },
                        {
                            link: `/appropriation/${ this.act.appropriation.id }`,
                            title: `Foranstaltning ${ this.act.appropriation.id }`
                        },
                        {
                            link: false,
                            title: `${ this.act.activity_type }`
                        }
                    ])
                })
                .catch(err => console.log(err))
            },
            reload: function() {
                this.show_edit =  false
            },
            displayDate: function(dt) {
                return json2js(dt)
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

    .activity .status-GRANTED {
        max-width: 6rem;
        background-color: var(--success);
        color: white;
        padding: .25rem;
    }

    .activity .status-EXPECTED {
        max-width: 6rem;
        background-color: var(--warning);
        color: white;
        padding: .25rem;
    }

</style>
