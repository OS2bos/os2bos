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
                    <fieldset>
                        <dl>
                            <dt>Foranstaltningssag</dt>
                            <dd>{{ appropriation.sbsys_id }}</dd>

                            <dt>SBSYS-hovedsag</dt>
                            <dd>{{ cas.sbsys_id }}</dd>

                            <dt>Sagspart (CPR, navn)</dt>
                            <dd>
                                {{ cas.cpr_number }}, {{ cas.name }}
                            </dd>
                        </dl>
                    </fieldset>

                    <fieldset class="payment-basic">
                        <legend>Hvad skal betales?</legend>

                        <label class="required" for="fieldSelectAct">Ydelse</label>
                        <p v-if="preselectedAct"><strong>{{ act_details[0].name }}</strong></p>
                        <list-picker v-if="!preselectedAct" :dom-id="'fieldSelectAct'" :disabled="disableAct" :selected-id="act.details" @selection="changeActivity" :list="act_details" required />
                        <error err-key="details" />

                        <label class="required" for="field-startdate">
                            Startdato
                            <span v-if="startDateSet && this.act.activity_type !== 'MAIN_ACTIVITY'">
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
                            <span v-if="endDateSet && this.act.activity_type !== 'MAIN_ACTIVITY'">
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
                    <pay-type-edit />
                    <pay-plan />
                </div>

                <div class="row-item">
                    <payment-receiver-edit />

                    <fieldset>
                        <input type="checkbox" id="field-fictive" v-model="payment.fictive">
                        <label for="field-fictive">Fiktiv Betaling</label>
                    </fieldset>
                </div>

            </div>

            <fieldset class="form-actions">
                <warning :content="payDateRule" />
                <input type="submit" value="Gem" :disabled="disableAct">
                <button class="cancel-btn" type="button" @click="cancel()">Annullér</button>
            </fieldset>

        </form>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import { activityId2name } from '../filters/Labels.js'
    import { epoch2DateStr, tenYearsAgo, inEighteenYears } from '../filters/Date.js'
    import { json2jsDate } from '../filters/Date.js'
    import Error from '../forms/Error.vue'
    import ListPicker from '../forms/ListPicker.vue'
    import PayTypeEdit from '../payment-details/payment-type/PaymentTypeEdit.vue'
    import PayPlan from '../payment-details/PaymentPlan.vue'
    import PaymentReceiverEdit from '../payment-details/payment-receiver/PaymentReceiverEdit.vue'
    import notify from '../notifications/Notify'
    import Warning from '../warnings/Warning.vue'
    import { checkRulePayDate } from '../filters/Rules.js'

    export default {

        components: {
            Error,
            ListPicker,
            PayTypeEdit,
            PayPlan,
            PaymentReceiverEdit,
            Warning
        },
        props: [
            'mode', // Can be either 'create', 'edit', or 'clone'
            'activityObj'
        ],
        data: function() {
            return {
                act: {},
                act_status_expected: false,
                act_details: null
            }
        },
        computed: {
            cas: function() {
                return this.$store.getters.getCase
            },
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
                    return epoch2DateStr(this.appropriation.granted_from_date)
                }
                if (this.mode === 'clone' && this.act.activity_type !== 'MAIN_ACTIVITY') {
                    this.act.start_date = null
                    return epoch2DateStr(this.appropriation.granted_from_date)
                }
                if (this.mode === 'clone' && this.act.activity_type === 'MAIN_ACTIVITY') {
                    this.act.start_date = null
                }
                return tenYearsAgo()
            },
            endDateSet: function() {
                if (this.act.activity_type !== 'MAIN_ACTIVITY' && this.mode !== 'clone') {
                    return epoch2DateStr(this.appropriation.granted_to_date)
                }
                if (this.mode === 'clone' && this.act.activity_type !== 'MAIN_ACTIVITY') {
                    this.act.end_date = null
                    return epoch2DateStr(this.appropriation.granted_to_date)
                }
                if (this.mode === 'clone' && this.act.activity_type === 'MAIN_ACTIVITY') {
                    this.act.end_date = null
                }
                return inEighteenYears()
            },
            payment: function() {
                return this.$store.getters.getPayment
            },
            payment_method: function() {
                return this.$store.getters.getPaymentMethod
            },
            payDateRule: function() {
                return checkRulePayDate(this.act.start_date, this.$store.getters.getPaymentMethod)
            },
            preselectedAct: function() {
                if (this.act_details && this.act_details.length === 1) {
                    this.$store.commit('setActDetail', this.act_details[0].id)
                    return this.act.details = this.act_details[0].id
                }
            }
        },
        watch: {
            activityObj: function() {
                this.update()
            },
            preselectedAct: function() {
                this.update()
            }
        },
        methods: {
            update: function() {
                this.$store.commit('clearPayment')
                if (this.activityObj) {
                    this.act = this.activityObj
                    this.$store.commit('setPayment', this.act.payment_plan)
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
            checkDateMax: function(datestr) {
                const maxpast = parseInt( new Date().getFullYear() ) - 10,
                    maxfuture = parseInt( new Date().getFullYear() ) + 18,
                    date_regex = /[0-9]{4}-[0-9]{2}-[0-9]{2}/g
                    
                if (!datestr.match(date_regex)) {
                    notify('Er du sikker på, at du har angivet dato som åååå-mm-dd?', 'error')
                    return false
                }
                if (parseInt(datestr.substr(0,4)) < maxpast) {
                    notify('Dato må maks. være 10 år tilbage i tiden', 'error')
                    return false
                } else if (parseInt(datestr.substr(0,4)) > maxfuture) {
                    notify('Dato må maks. være 18 år fremme i tiden', 'error')
                    return false
                } else {
                    return true
                }
            },
            saveChanges: function() {
                if (!this.checkDateMax(this.act.start_date)) {
                    return
                }
                if (this.act.end_date && !this.checkDateMax(this.act.end_date)) {
                    return
                }
                let data = {
                    activity_type: this.act.activity_type,
                    start_date: this.act.start_date,
                    end_date: this.act.end_date ? this.act.end_date : null,
                    details: this.act.details,
                    note: this.act.note,
                    payment_plan: this.payment
                }
                if (this.payment.payment_type === 'ONE_TIME_PAYMENT') {
                    data.end_date = data.start_date
                }
                if (this.mode === 'create') {
                    data.appropriation = this.$route.params.apprid
                    data.status = this.act_status_expected ? 'EXPECTED' : 'DRAFT'
                    data.payment_plan.id = null
                } else if (this.mode === 'clone') {
                    data.appropriation = this.activityObj.appropriation
                    data.modifies = this.act.id
                    data.status = 'EXPECTED'
                    data.payment_plan.id = null
                } else {
                    data.id = this.act.id
                    data.appropriation = this.activityObj.appropriation
                }

                if (this.mode === 'create' || this.mode === 'clone') {
                    
                    // POSTING an activity
                    axios.post(`/activities/`, data)
                    .then(res => {
                        this.$router.push(`/appropriation/${ this.appropriation.id }`)
                        this.$store.dispatch('fetchActivity', res.data.id)
                        this.$store.commit('clearPayment')
                    })
                    .catch(err => this.$store.dispatch('parseErrorOutput', err))

                } else {

                    // PATCHING an activity
                    axios.patch(`/activities/${ this.act.id }/`, data)
                    .then(res => {
                        this.$router.push(`/appropriation/${ this.appropriation.id }`)
                        this.$store.dispatch('fetchActivity', res.data.id)
                        this.$store.commit('clearPayment')
                    })
                    .catch(err => this.$store.dispatch('parseErrorOutput', err))
                }
            },
            cancel: function() {
                this.$store.commit('clearPayment')
                if (this.mode !== 'create') {
                    // Fetch activity anew, since store should be polluted with cancelled edit info
                    this.$store.dispatch('fetchActivity', this.act.id) 
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
                    actList = `supplementary_activity_for=${ this.appropriation.section }&main_activities=${ this.appr_main_acts.activities[0].details }`
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