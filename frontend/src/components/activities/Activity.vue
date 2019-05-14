<template>

    <section class="activity" v-if="act">
        <header class="activity-header">
            <h1>Aktivitet, {{ act.activity }}</h1>
            <button v-if="!show_edit" @click="show_edit = true" class="act-edit-btn">Redigér</button>
        </header>

        <div v-if="show_edit">
            <activity-edit :activity-data="act" @cancelled="show_edit = false" @saved="show_edit = false" />
        </div>

        <div v-if="!show_edit">
            <dl>
                <dt>Status</dt>
                <dd>
                    <div v-if="act.is_estimated_cost">Forventning</div>
                    <div v-if="!act.is_estimated_cost">Bevilling</div>
                </dd>
                <dt>Type</dt>
                <dd>
                    <div v-if="act.is_main_act">Hovedaktivitet</div>
                    <div v-if="!act.is_main_act">Tillægsydelse</div>
                    <div v-if="act.is_single_payment">Enkeltudgift</div>
                    <div v-if="!act.is_single_payment">Følgeydelse </div>
                </dd>
                <dt>Bevilling efter </dt>
                <dd>{{ act.law_ref }}</dd>
                <dt>Aktivitet</dt>
                <dd>{{ act.activity }}</dd>
                <dt>Startdato</dt>
                <dd>{{ new Date(act.startdate).toLocaleDateString() }}</dd>
                <dt>Slutdato</dt>
                <dd>{{ new Date(act.enddate).toLocaleDateString() }}</dd>
            </dl>
            <h2>Udgifter</h2>
            <dl>
                <dt>Beløb</dt>
                <dd>{{ act.payment.amount }} kr</dd>
                <dt>Afregningsenhed</dt>
                <dd>
                    <template v-if="!act.is_single_payment">
                        <p>Kroner pr. måned</p>
                        <p>Første år {{ act.payment.amount * 12  }} kr</p>
                        <p>Årligt {{ act.payment.amount * 12 }} kr</p>
                    </template>
                    <template v-if="act.is_single_payment">
                        <p>Enkeltudgift</p>
                    </template>
                </dd>
                <dt>Bemærkninger</dt>
                <dd>{{ act.payment.note }}</dd>
            </dl>
            <h3>Betalingsmodtager</h3>
            <dl>
                <dt>Type</dt>
                <dd>{{ act.payment.payee.type }}</dd>
                <dt>ID</dt>
                <dd>{{ act.payment.payee.id }}</dd>
                <dt>Navn</dt>
                <dd>{{ act.payment.payee.name }}</dd>
                <dt>Betalingsmåde</dt>
                <dd>
                    {{ act.payment.method.type }}
                    <span v-if="act.payment.method.type === 'SD-løn'">
                        ({{ act.payment.method.skattekort }})
                    </span>
                </dd>
            </dl>
        </div>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import ActivityEdit from './ActivityEdit.vue'

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
            fetch_appr: function(id) {
                axios.get('../../activity-1-data.json')
                .then(res => {
                    this.act = res.data
                    this.$store.commit('setBreadcrumb', [
                        {
                            link: '/',
                            title: 'Mine sager'
                        },
                        {
                            link: `/case/${ this.act.appropriation.case.pk }`,
                            title: `Sag ${ this.act.appropriation.sbsys_id }`
                        },
                        {
                            link: `/appropriation/${ this.act.appropriation.pk }`,
                            title: `Bevilling ${ this.act.appropriation.sbsys_id }`
                        },
                        {
                            link: false,
                            title: `${ this.act.activity }`
                        }
                    ])
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
