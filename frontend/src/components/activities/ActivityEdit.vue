<template>
    <section class="activity">
        <form @submit.prevent="saveChanges()">
        <h1 v-if="create_mode">Opret Aktivitet</h1>
        <h1 v-else>Redigér Aktivitet</h1>

        <div class="row">
            <div class="column">
                <fieldset>
                    <legend>Status</legend>
                    <input type="checkbox" id="field-status-expected" v-model="act_status_expected">
                    <label for="field-status-expected">Forventning</label>
                </fieldset>
                <fieldset>
                    <legend>Type</legend>
                    <input type="radio" id="field-type-main" value="MAIN_ACTIVITY" v-model="act.activity_type">
                    <label for="field-type-main">Foranstaltningsudgift</label>
                    <input type="radio" id="field-type-suppl" value="SUPPL_ACTIVITY" v-model="act.activity_type">
                    <label for="field-type-suppl">Følgeudgift</label>
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
                <payment-amount-edit v-model="pay.payment_amount"/>
                <payment-receiver-edit v-model="pay.payment_receiver"/>
                <payment-edit v-model="pay.payment"/>

                <hr>
                <fieldset>
                    <input type="submit" value="Gem">
                    <button class="cancel-btn" type="button" @click="cancel()">Annullér</button>
                </fieldset>
            </div>

            <div class="column"></div>
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
            'activityObj'
        ],
        data: function() {
            return {
                act: {},
                act_status_expected: false,
                pay: {
                    payment_amount: {},
                    payment_receiver: {},
                    payment: {}
                },
                create_mode: true
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
                let data = {
                    activity_type: this.act.activity_type,
                    start_date: this.act.start_date,
                    end_date: this.act.end_date,
                    details: this.act.details,
                    note: this.act.note
                }
                 let data_payee = {
                    recipient_type: this.pay.payment_receiver.selected,
                    recipient_id: this.pay.payment_receiver.payee_id,
                    recipient_name: this.pay.payment_receiver.payee_name,
                    payment_method: this.pay.payment.selected,
                    payment_frequency: this.pay.payment_amount.frequency,
                    payment_type: this.pay.payment_amount.type,
                    payment_units: this.pay.payment_amount.units,
                    payment_amount: this.pay.payment_amount.amount
                }
                data.status = this.act_status_expected ? 'EXPECTED' : 'GRANTED'
                if (!this.create_mode) {
                    data.id = this.act.id
                    data.appropriation = this.activityObj.appropriation
                    axios.patch(`/activities/${ this.act.id }/`, data)
                    .then(res => {
                        this.$emit('save', res.data)
                        axios.patch(`/payment_schedules/${ this.act.payment_plan }/`, data_payee)
                        .then(resp => {
                            axios.patch(`/activities/${ res.data.id }/`, {
                                payment_plan: resp.data.id
                            })
                        })
                    })
                        .catch(err => console.log(err))
                } else {
                    const appr_id = this.$route.params.apprid
                    data.appropriation = appr_id
                    axios.post(`/activities/`, data)
                    .then(res => {
                        this.$router.push(`/appropriation/${ appr_id }`)
                        axios.post(`/payment_schedules/`, data_payee)
                        .then(resp => {
                            axios.patch(`/activities/${ res.data.id }/`, {
                                payment_plan: resp.data.id
                            })
                        })
                    })
                    .catch(err => console.log(err))
                }
            },
            cancel: function() {
                if (!this.create_mode) {
                    this.$emit('close')
                } else {
                    this.$router.push(`/appropriation/${ this.$route.params.apprid }`)
                }  
            }
        },
        created: function() {
            if (this.activityObj) {
                this.create_mode = false
                this.act = this.activityObj
            }
        }
    }
    
</script>

<style>

    .activity {
        margin: 1rem;
    }

    .activity .cancel-btn {
        margin-left: 0.5rem;
        background-color: transparent;
        color: var(--primary);
        border-color: transparent;
    }

    .activity.expectation {
        border: solid 3px var(--danger);
    }

</style>