<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <section :class="`activity-edit activity-${ mode } expected-${ act_status_expected }`">
        <header class="header" v-if="mode === 'create'">
            <h1>
                <template v-if="act_status_expected">
                    Tilføj forventet
                </template>
                <template v-else>
                    Tilføj
                </template>
                <template v-if="main_act">
                    følgeydelse
                </template>
                <template v-else>
                    aktivitet
                </template>
            </h1>
        </header>
        <header class="header" v-if="mode === 'edit'">
            <h1>Redigér Aktivitet</h1>
        </header>
        <header class="header" v-if="mode === 'clone'">
            <h1>Opret forventet justering</h1>
            <p>
                Du er ved at lave en forventet justering til aktiviteten:<br> 
                <strong>{{ displayActName(act.details) }}</strong>
            </p>
        </header>
        <form @submit.prevent="saveChanges()">
            <div class="row">
                <div class="column">
                    <fieldset v-if="mode === 'create'">
                        <input type="checkbox" id="field-status-expected" v-model="act_status_expected">
                        <label for="field-status-expected">Opret forventet aktivitet</label>
                    </fieldset>
                    <fieldset v-if="mode === 'create' && !main_act">
                        <legend>Type</legend>
                        <input type="radio" id="field-type-main" value="MAIN_ACTIVITY" name="activity" v-model="act.activity_type" @change='activityList()' required>
                        <label for="field-type-main">Hovedydelse</label>
                        <input type="radio" id="field-type-suppl" value="SUPPL_ACTIVITY" name="activity" v-model="act.activity_type" @change='activityList()'>
                        <label for="field-type-suppl">Følgeydelse</label>
                    </fieldset>
                    <dl v-else>
                        <dt>Type</dt>
                        <dd>Følgeydelse</dd>
                    </dl>
                    <fieldset>
                        <label for="fieldSelectAct">Aktivitet</label>
                        <list-picker :dom-id="'fieldSelectAct'" :disabled="disableAct" :selected-id="act.details" @selection="changeActivity" :list="act_details" required/>
                    </fieldset>
                    <fieldset>
                        <label for="field-startdate">Startdato</label>
                        <input type="date" id="field-startdate" v-model="act.start_date" :max="current_end_date" @change="setMinMaxDates()" required>
                    </fieldset>
                    <fieldset>
                        <label for="field-enddate">Slutdato</label>
                        <input type="date" id="field-enddate" v-model="act.end_date" :min="current_start_date" @change="setMinMaxDates()">
                    </fieldset>
                    <fieldset>
                        <label for="field-text">Supplerende information</label>
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
    import { activityId2name } from '../filters/Labels.js'

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
                pay: {},
                act_details: null,
                current_start_date: null,
                current_end_date: null
            }
        },
        computed: {
            appropriation: function() {
                return this.$store.getters.getAppropriation
            },
            disableAct: function () {
                if (this.act_details < 1) {
                    return true
                }
            },
            main_act: function() {
                if (this.appropriation) {
                    let act = false
                    for (let a of this.appropriation.activities) {
                        if (a.activity_type === 'MAIN_ACTIVITY') {
                            act = a
                        }
                    }
                    if (act) {
                        this.act.activity_type = 'SUPPL_ACTIVITY'
                        this.activityList()
                        if (!this.act.start_date) {
                            this.act.start_date = act.start_date
                        }
                        if (!this.act.end_date) {
                            this.act.end_date = act.end_date
                        }
                    }
                    return act
                } else {
                    return false
                }
            }
        },
        methods: {
            changeActivity: function(act) {
                this.act.details = act
                this.$store.commit('setActDetail', act)
            },
            setMinMaxDates: function() {
                if (this.act.start_date) {
                    this.current_start_date = this.act.start_date
                }
                if (this.act.end_date) {
                    this.current_end_date = this.act.end_date
                }
            },
            displayActName: function(id) {
                return activityId2name(id)
            },
            saveChanges: function() {
                
                let data = {
                    activity_type: this.act.activity_type,
                    start_date: this.act.start_date,
                    end_date: this.act.end_date,
                    details: this.act.details,
                    note: this.act.note,
                    payment_plan: {
                        recipient_type: this.pay.recipient_type,
                        recipient_id: this.pay.recipient_id,
                        recipient_name: this.pay.recipient_name,
                        payment_method: this.pay.payment_method,
                        payment_frequency: this.pay.payment_frequency,
                        payment_type: this.pay.payment_type,
                        payment_units: this.pay.payment_units,
                        payment_amount: this.pay.payment_amount,
                        payment_method_details: parseInt(this.pay.payment_method_details)
                    }
                }

                if (this.mode === 'create') {
                    data.appropriation = this.$route.params.apprid
                    data.status = this.act_status_expected ? 'EXPECTED' : 'DRAFT'
                } else if (this.mode === 'clone') {
                    data.appropriation = this.activityObj.appropriation
                    data.modifies = this.act.id
                    data.status = 'EXPECTED'
                } else {
                    data.id = this.act.id
                    data.payment_plan.id = this.act.payment_plan.id
                    data.appropriation = this.activityObj.appropriation
                }

                if (this.mode === 'create' || this.mode === 'clone') {
                    // POSTING an activity

                    axios.post(`/activities/`, data)
                    .then(res => {
                        this.$router.push(`/appropriation/${ this.appropriation.id }`)
                        this.$store.dispatch('fetchActivity', res.data.id)
                    })
                    .catch(err => console.log(err))

                } else {
                    // PATCHING an activity

                    axios.patch(`/activities/${ this.act.id }/`, data)
                    .then(res => {
                        this.$router.push(`/appropriation/${ this.appropriation.id }`)
                        this.$store.dispatch('fetchActivity', res.data.id)
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
            activityList: function() {
                let actList
                if (this.act.activity_type === 'MAIN_ACTIVITY') {
                    actList = `main_activity_for=${ this.appropriation.section }`
                } else {
                    actList = `supplementary_activity_for=${ this.appropriation.section }`
                }
                axios.get(`/activity_details?${ actList }`)
                .then(res => {
                    this.act_details = res.data
                })
                .catch(err => console.log(err))
            }
        },
        created: function() {
            if (this.activityObj) {
                this.act = this.activityObj
                this.pay = this.act.payment_plan
                this.activityList()
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