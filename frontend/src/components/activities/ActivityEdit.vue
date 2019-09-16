<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <section :class="`activity-edit activity-${ mode } expected-${ act_status_expected }`">
        <form @submit.prevent="saveChanges()">
            <header class="header activity-edit-header"> 

                <h1 v-if="mode === 'create'">
                    <template v-if="act_status_expected">Tilføj forventet </template>
                    <template v-else>Tilføj </template>
                    <template v-if="!appr_main_acts">hovedydelse</template>
                    <template v-else>følgeydelse</template>
                </h1>
                <h1 v-if="mode === 'edit'">Redigér Ydelse</h1>
                <div v-if="mode === 'clone'">
                    <h1>Opret forventet justering</h1>
                    <p>
                        Du er ved at lave en forventet justering til ydelsen:<br> 
                        <strong>{{ displayActName(act.details) }}</strong>
                    </p>
                </div>

                <fieldset v-if="mode === 'create'" style="margin: 0 0 0 2rem;">
                    <input type="checkbox" id="field-status-expected" v-model="act_status_expected">
                    <label for="field-status-expected" style="margin: 0;">Opret forventet Ydelse</label>
                </fieldset>

            </header>
        
            <error />

            <div class="row">
                        
                <div class="row-item">
                    <fieldset class="payment-basic">
                        <legend>Hvad skal betales?</legend>

                        <label class="required" for="fieldSelectAct">Ydelse</label>
                        <list-picker :dom-id="'fieldSelectAct'" :disabled="disableAct" :selected-id="act.details" @selection="changeActivity" :list="act_details" required />
                        <error err-key="details" />
                        <label class="required" for="field-startdate">
                            Startdato
                            <span v-if="startDateSet">
                                - tidligst {{ displayDate(startDateSet) }}
                            </span>
                        </label>
                        <input 
                            type="date" 
                            id="field-startdate" 
                            v-model="act.start_date" 
                            :max="endDateSet"
                            :min="startDateSet" 
                            pattern="[0-9]{4}-[0-9]{2}-[0-9]{2}"
                            placeholder="åååå-mm-dd"
                            required>
                        <error err-key="start_date" />
                    
                        <label for="field-enddate">
                            Slutdato
                            <span v-if="endDateSet">
                                - senest {{ displayDate(endDateSet) }}
                            </span>
                        </label>
                        <input 
                            type="date" 
                            id="field-enddate" 
                            v-model="act.end_date" 
                            :max="endDateSet"
                            :min="startDateSet"
                            pattern="[0-9]{4}-[0-9]{2}-[0-9]{2}"
                            placeholder="åååå-mm-dd">
                    
                        <label for="field-text">Supplerende information</label>
                        <textarea id="field-text" v-model="act.note" style="height: 8rem;"></textarea>
                    </fieldset>
                </div>

                <div class="row-item">
                    <pay-type-edit :pay.sync="pay" />
                    <pay-freq-edit :pay.sync="pay" />
                    <pay-amount-edit :pay.sync="pay" />
                    <pay-plan v-if="pay.payment_amount" :amount="pay.payment_amount" :units="pay.payment_units" :type="pay.payment_type" :frequency="pay.payment_frequency" />
                </div>

                <div class="row-item">
                    <pay-payee-edit :pay.sync="pay" />
                    <pay-mean-edit :pay.sync="pay" />
                </div>

            </div>

            <fieldset class="form-actions">
                <input type="submit" value="Gem" :disabled="disableAct">
                <button class="cancel-btn" type="button" @click="cancel()">Annullér</button>
            </fieldset>

        </form>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import { activityId2name } from '../filters/Labels.js'
    import { epoch2DateStr } from '../filters/Date.js'
    import { json2jsDate } from '../filters/Date.js'
    import Error from '../forms/Error.vue'
    import ListPicker from '../forms/ListPicker.vue'
    import PayTypeEdit from '../payment/PaymentTypeEdit.vue'
    import PayFreqEdit from '../payment/PaymentFrequencyEdit.vue'
    import PayAmountEdit from '../payment/PaymentAmountEdit.vue'
    import PayPayeeEdit from '../payment/PaymentPayeeEdit.vue'
    import PayMeanEdit from '../payment/PaymentMeansEdit.vue'
    import PayPlan from '../payment/PaymentPlan.vue'

    export default {

        components: {
            Error,
            ListPicker,
            PayTypeEdit,
            PayFreqEdit,
            PayAmountEdit,
            PayMeanEdit,
            PayPayeeEdit,
            PayPlan
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
                act_details: null
            }
        },
        computed: {
            appropriation: function() {
                return this.$store.getters.getAppropriation
            },
            appr_main_acts: function() {
                return this.$store.getters.getAppropriationMainActs
            },
            disableAct: function () {
                if (this.act_details && this.act_details.length < 1) {
                    return true
                }
            },
            startDateSet: function() {
                if (this.act.activity_type !== 'MAIN_ACTIVITY' && this.mode !== 'clone') {
                    return epoch2DateStr(this.appr_main_acts.start_date)
                }
                if (this.mode === 'clone' && this.act.activity_type !== 'MAIN_ACTIVITY') {
                    this.act.start_date = null
                    return epoch2DateStr(this.appr_main_acts.start_date)
                }
                if (this.mode === 'clone' && this.act.activity_type === 'MAIN_ACTIVITY') {
                    this.act.start_date = null
                }
                return false
            },
            endDateSet: function() {
                if (this.act.activity_type !== 'MAIN_ACTIVITY' && this.mode !== 'clone') {
                    return epoch2DateStr(this.appr_main_acts.end_date)
                }
                if (this.mode === 'clone' && this.act.activity_type !== 'MAIN_ACTIVITY') {
                    this.act.end_date = null
                    return epoch2DateStr(this.appr_main_acts.end_date)
                }
                if (this.mode === 'clone' && this.act.activity_type === 'MAIN_ACTIVITY') {
                    this.act.end_date = null
                }
                return false
            }
        },
        watch: {
            activityObj: function() {
                this.update()
            }
        },
        methods: {
            update: function() {
                if (this.activityObj) {
                    this.act = this.activityObj
                    this.pay = this.act.payment_plan
                } else {
                    if (!this.appr_main_acts) {
                        this.act.activity_type = 'MAIN_ACTIVITY'
                    } else {
                        this.act.activity_type = 'SUPPL_ACTIVITY'
                    }
                }
                this.activityList()
            },
            changeActivity: function(act) {
                this.act.details = act
                this.$store.commit('setActDetail', act)
            },
            displayActName: function(id) {
                return activityId2name(id)
            },
            displayDate: function(dt) {
                return json2jsDate(dt)
            },
            saveChanges: function() {
                let data = {
                    activity_type: this.act.activity_type,
                    start_date: this.act.start_date,
                    end_date: this.act.end_date ? this.act.end_date : null,
                    details: this.act.details,
                    note: this.act.note,
                    payment_plan: this.pay
                }
                if (this.pay.payment_type === 'ONE_TIME_PAYMENT') {
                    data.end_date = data.start_date
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
                    .catch(err => this.$store.dispatch('parseErrorOutput', err))

                } else {
                    // PATCHING an activity

                    axios.patch(`/activities/${ this.act.id }/`, data)
                    .then(res => {
                        this.$router.push(`/appropriation/${ this.appropriation.id }`)
                        this.$store.dispatch('fetchActivity', res.data.id)
                    })
                    .catch(err => this.$store.dispatch('parseErrorOutput', err))
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
                axios.get(`/activity_details/?${ actList }`)
                .then(res => {
                    this.act_details = res.data
                })
                .catch(err => console.log(err))
            }
        },
        created: function() {
            this.update()
            this.$store.commit('clearErrors')
        }
    }
    
</script>

<style>

    .activity-edit {
        margin: 1rem 2rem 2rem;
        background-color: var(--grey1);
    }

    .activity-edit .activity-edit-header {
        background-color: var(--grey2);
        padding: .5rem 2rem;
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
    }

    .activity-edit.activity-clone,
    .activity-edit.expected-true {
        background-color: hsl(40, 90%, 80%);
    }

    .activity-edit.activity-clone .activity-edit-header,
    .activity-edit.expected-true .activity-edit-header {
        background-color: hsl(40, 90%, 70%);
    }

    .activity-edit form {
        background-color: transparent;
        padding: 0;
    }

    .activity-edit .row-item {
        margin: 0;
        padding: 1rem 2rem 2rem;
        border: solid 1px var(--grey2);
    }

    .activity-edit select {
        width: 100%;
    }

    .activity-edit .payment-amount > * {
        flex: 0 1 15rem;
        border: none;
    }

    .activity-edit .payment-payee,
    .activity-edit .payment-means {
        max-width: 30rem;
        border: none;
        margin: 0;
        padding: 0;
    }

    .activity-edit .payment-means {
        margin-top: 1rem;
    }

    .activity-edit .payment-plan {
        border: solid .25rem hsl(40, 90%, 70%);
        background-color: hsl(40, 90%, 80%);
    }

    .activity-edit .form-actions {
        padding: 2rem 2rem 2rem;
    }

    .activity-edit .cancel-btn {
        margin-left: 0.5rem;
        background-color: transparent;
        color: var(--primary);
        border-color: transparent;
    }

</style>