<template>
    <section :class="`activity-edit activity-${ mode } expected-${ act_status_expected }`">
        <header class="header" v-if="mode === 'create'">
            <h1>Opret Aktivitet</h1>
        </header>
        <header class="header" v-if="mode === 'edit'">
            <h1>Redigér Aktivitet</h1>
        </header>
        <header class="header" v-if="mode === 'clone'">
            <h1>Opret forventet justering</h1>
            <p>Du er ved at lave en forventet justering til aktiviteten {{ act.details }}.</p>
        </header>
        <form @submit.prevent="saveChanges()">
            <div class="row">
                <div class="column">
                    <fieldset v-if="mode === 'create'">
                        <input type="checkbox" id="field-status-expected" v-model="act_status_expected">
                        <label for="field-status-expected">Opret som forventet justering</label>
                    </fieldset>
                    <fieldset v-if="mode === 'create'">
                        <legend>Type</legend>
                        <input type="radio" id="field-type-main" value="MAIN_ACTIVITY" v-model="act.activity_type">
                        <label for="field-type-main">Hovedydelse</label>
                        <input type="radio" id="field-type-suppl" value="SUPPL_ACTIVITY" v-model="act.activity_type">
                        <label for="field-type-suppl">Følgeydelse</label>
                    </fieldset>
                    <fieldset>
                        <label for="selectField">Aktivitet</label>
                        <list-picker :dom-id="'selectField'" :selected-id="act.details" @selection="changeActivity" :list="activities" />
                    </fieldset>
                    <fieldset>
                        <label for="field-startdate">Startdato</label>
                        <input type="date" id="field-startdate" v-model="act.start_date">
                    </fieldset>
                    <fieldset>
                        <label for="field-enddate">Slutdato</label>
                        <input type="date" id="field-enddate" v-model="act.end_date">
                    </fieldset>
                    <fieldset>
                        <label for="field-text">Bemærkning</label>
                        <textarea v-model="act.note"></textarea>
                    </fieldset>
                    <hr>
                    <payment-amount-edit :payment-obj="pay" />
                    <payment-receiver-edit :payment-obj="pay" />
                    <payment-edit :payment-obj="pay" />
                    <hr>
                    <fieldset>
                        <input type="submit" value="Gem">
                        <button class="cancel-btn" type="button" @click="cancel()">Annullér</button>
                    </fieldset>
                </div>
            </div>
        </form>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import ListPicker from '../forms/ListPicker.vue'
    import PaymentAmountEdit from '../payment/PaymentAmountEdit.vue'
    import PaymentReceiverEdit from '../payment/PaymentReceiverEdit.vue'
    import PaymentEdit from '../payment/PaymentEdit.vue'

    export default {

        components: {
            ListPicker,
            PaymentAmountEdit,
            PaymentReceiverEdit,
            PaymentEdit
        },
        props: [
            'mode', // Can be either 'create', 'edit', or 'clone'
            'activityObj'
        ],
        data: function() {
            return {
                act: {},
                act_status_expected: false,
                pay: {}
            }
        },
        computed: {
            activities: function() {
                return this.$store.getters.getActivities
            }
        },
        methods: {
            changeActivity: function(act) {
                this.act.details = act
            },
            saveChanges: function() {
                
                const appr_id = this.$route.params.apprid
                let data = {
                        activity_type: this.act.activity_type,
                        start_date: this.act.start_date,
                        end_date: this.act.end_date,
                        details: this.act.details,
                        note: this.act.note
                    },
                    data_payee = {
                        recipient_type: this.pay.recipient_type,
                        recipient_id: this.pay.recipient_id,
                        recipient_name: this.pay.recipient_name,
                        payment_method: this.pay.payment_method,
                        payment_frequency: this.pay.payment_frequency,
                        payment_type: this.pay.payment_type,
                        payment_units: this.pay.payment_units,
                        payment_amount: this.pay.payment_amount
                    }

                if (this.mode === 'create') {
                    data.appropriation = appr_id
                    data.status = this.act_status_expected ? 'EXPECTED' : 'DRAFT'
                } else if (this.mode === 'clone') {
                    data.appropriation = this.activityObj.appropriation
                    data.modifies = this.act.id
                    data.status = 'EXPECTED'
                } else {
                    data.id = this.act.id
                    data.appropriation = this.activityObj.appropriation
                }

                if (this.mode === 'create' || this.mode === 'clone') {
                    // POSTING an activity

                    axios.post(`/activities/`, data)
                    .then(res => {
                        this.$router.push(`/appropriation/${ appr_id }`)
                        axios.post(`/payment_schedules/`, data_payee)
                        .then(resp => {
                            axios.patch(`/activities/${ res.data.id }/`, {
                                payment_plan: resp.data.id
                            })
                            .then(() => {
                                this.$store.dispatch('fetchActivity', res.data.id)
                            })
                        })
                    })
                    .catch(err => console.log(err))

                } else {
                    // PATCHING an activity

                    axios.patch(`/activities/${ this.act.id }/`, data)
                    .then(res => {
                        this.$emit('save', res.data)
                        axios.patch(`/payment_schedules/${ this.act.payment_plan }/`, data_payee)
                        .then(resp => {
                            axios.patch(`/activities/${ res.data.id }/`, {
                                payment_plan: resp.data.id
                            })
                            .then(() => {
                                this.$store.dispatch('fetchActivity', res.data.id)
                            })
                        })
                    })
                    .catch(err => console.log(err))

                }
            },
            cancel: function() {
                if (this.mode !== 'create') {
                    this.$emit('close')
                } else {
                    this.$router.push(`/appropriation/${ this.$route.params.apprid }`)
                }  
            },
            fetchPaymentInfo: function(pay_plan_id) {
                axios.get(`/payment_schedules/${ pay_plan_id }/`)
                .then(res => {
                    this.pay = res.data
                })
                .catch(err => console.log(err))
            }
        },
        created: function() {
            console.log(this.mode)
            if (this.activityObj) {
                this.act = this.activityObj
                this.fetchPaymentInfo(this.activityObj.payment_plan)
            }
        }
    }
    
</script>

<style>

    .activity-edit {
        margin: 1rem;
        background-color: var(--grey1);
    }

    .activity-edit > header {
        background-color: var(--grey2);
        padding: 1rem;
    }

    .activity-edit.activity-clone,
    .activity-edit.expected-true {
        background-color: hsl(40, 90%, 80%);
    }

    .activity-edit.activity-clone > header,
    .activity-edit.expected-true > header {
        background-color: hsl(40, 90%, 70%);
    }

    .activity-edit form {
        background-color: transparent;
    }

    .activity-edit .cancel-btn {
        margin-left: 0.5rem;
        background-color: transparent;
        color: var(--primary);
        border-color: transparent;
    }

</style>