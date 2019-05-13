<template>

    <section class="activity" v-if="act">
        <h1>Aktivitet</h1>
        <dl>
            <dt>Status</dt>
            <dd>{{ act.status }}</dd>
            <dt>Type</dt>
            <dd>
                <span v-for="c in act.classifications">{{ c }} </span>
            </dd>
            <dt>Bevilling efter </dt>
            <dd>{{ act.law_ref }}</dd>
            <dt>Aktivitet</dt>
            <dd>{{ act.activity }}</dd>
            <dt>Startdato</dt>
            <dd>{{ new Date(act.startdate).toLocaleDateString() }}</dd>
            <dt>Slutdato</dt>
            <dd>{{ new Date(act.enddate).toLocaleDateString() }}</dd>
            <dt>Bemærkninger</dt>
            <dd>{{ act.note }}</dd>
        </dl>
        <h2>Udgifter</h2>
        <dl>
            <dt>Beløb</dt>
            <dd>{{ act.payment.amount }}</dd>
            <dt>Afregningsenhed</dt>
            <dd>
                <template v-if="act.payment.payment_freq === 'monthly'">
                    <p>Kroner pr. måned</p>
                    <p>Første år {{ act.payment.amount * 12  }}</p>
                    <p>Årligt {{ act.payment.amount * 12 }}</p>
                </template>
            </dd>
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
    </section>

</template>

<script>

    import axios from '../http/Http.js'

    export default {

        data: function() {
            return {
                act: null
            }
        },
        methods: {
            fetch_appr: function(id) {
                axios.get('../../activity-1-data.json')
                .then(res => {
                    this.act = res.data
                })
                .catch(err => console.log(err))
            },
            setBreadCrumb: function() {

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

</style>
