<template>
    <article class="activity-edit">
        <form @submit.prevent="saveChanges()">
        <h1 v-if="create_mode">Opret Aktivitet</h1>
        <h1 v-else>Redigér Aktivitet</h1>

            <fieldset>
                <legend>Status</legend>
                <input type="radio" id="field-status-granted" value="GRANTED" v-model="act.status">
                <label for="field-status-granted">Bevilling</label>
                <input type="radio" id="field-status-expected" value="EXPECTED" v-model="act.status">
                <label for="field-status-expected">Forventning</label>
            </fieldset>
            <fieldset>
                <legend>Type</legend>
                <input type="radio" id="field-type-main" value="MAIN_ACTIVITY" v-model="act.activity_type">
                <label for="field-type-main">Hovedaktivitet</label>
                <input type="radio" id="field-type-suppl" value="SUPPL_ACTIVITY" v-model="act.activity_type">
                <label for="field-type-suppl">Følgeaktivitet</label>
                <input type="radio" id="field-type-expected" value="EXPECTED_CHANGE" v-model="act.activity_type">
                <label for="field-type-expected">Forventning</label>
            </fieldset>
            <fieldset>
                <strong>Bevilling efter §</strong>
                <span> ikke implementeret</span>
            </fieldset>
            <fieldset>
                <label for="selectField">Aktivitet</label>
                <list-picker :dom-id="'selectField'" :selected-id="act.service" @selection="changeActivity" :list="activities" />
            </fieldset>
            <fieldset>
                <label for="field-startdate">Startdato</label>
                <input type="date" id="field-startdate" v-model="act.start_date">
            </fieldset>
            <fieldset>
                <label for="field-enddate">Slutdato</label>
                <input type="date" id="field-enddate" v-model="act.end_date">
            </fieldset>
            <hr>
            <fieldset>
                <label for="field-cost">Bevilget beløb</label>
                <input type="number" id="field-cost" value="0">
            </fieldset>
            <fieldset>
                <legend>Udgiftstype</legend>
                <input type="radio" id="field-cost-single" :value="false">
                <label for="field-cost-single">Følgeydelse</label>
                <input type="radio" id="field-cost-recurring" :value="true">
                <label for="field-cost-recurring">Enkeltudgift</label>
            </fieldset>
            <fieldset>
                <label for="field-note">Bemærkning</label>
                <textarea id="field-note"></textarea>
            </fieldset>
            <hr>
            <fieldset>
                <legend>Betalingsmodtager</legend>
                <input type="radio" id="field-payment-type-inherit" value="inherit">
                <label for="field-payment-type-inherit">Samme som hovedydelsen</label>
                <input type="radio" id="field-payment-type-intern" value="intern">
                <label for="field-payment-type-intern">Intern</label>
                <input type="radio" id="field-payment-type-person" value="person">
                <label for="field-payment-type-person">Person</label>
                <input type="radio" id="field-payment-type-firm" value="firma">
                <label for="field-payment-type-firm">Firma</label>
            </fieldset>
            <template>
                <fieldset>
                    <label for="field-payment-id">
                        <template>CPR-nr/</template>
                        <template>CVR-nr </template>
                        <template>Reference</template>
                    </label>
                    <input type="text" id="field-payment-id" value="Ukendt">
                </fieldset>
                <fieldset>
                    <label for="field-payment-name">Navn</label>
                    <input type="text" id="field-payment-name" value="Ukendt">
                </fieldset>
                <fieldset>
                    <legend>Betalingsmåde</legend>
                    <input type="radio" id="field-payment-method-cash" value="kontant">
                    <label for="field-payment-method-cash">Kontant udbetaling</label>
                    <input type="radio" id="field-payment-method-sd" value="SD-løn">
                    <label for="field-payment-method-sd">SD-løn</label>
                    <input type="radio" id="field-payment-method-invoice" value="faktura">
                    <label for="field-payment-method-invoice">Faktura</label>
                    <input type="radio" id="field-payment-method-internal" value="intern afregning">
                    <label for="field-payment-method-internal">Intern afregning</label>
                </fieldset>
            </template>
            <hr>
            <fieldset>
                <input type="submit" value="Gem">
                <button class="cancel-btn" type="button" @click="cancel()">Annullér</button>
            </fieldset>
        </form>
    </article>

</template>

<script>

    import axios from '../http/Http.js'
    import ListPicker from '../forms/ListPicker.vue'

    export default {

        components: {
            ListPicker
        },
        props: [
            'activityObj'
        ],
        data: function() {
            return {
                act: {},
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
                this.act.service = act
            },
            cancel: function() {
                if (!this.create_mode) {
                    this.$emit('close')
                } else {
                    this.$router.push('/')
                }  
            },
            saveChanges: function() {
                let data = {
                    appropriation: this.activityObj.appropriation,
                    status: this.act.status,
                    activity_type: this.act.activity_type,
                    id: this.act.id,
                    start_date: this.act.start_date,
                    end_date: this.act.end_date,
                    service: this.act.service
                }
                if (!this.create_mode) {
                    axios.patch(`/activities/${ this.act.id }/`, data)
                    .then(res => {
                        this.$emit('save', res.data)
                    })
                    .catch(err => console.log(err))
                } else {
                    const appr_id = this.$route.params.apprid
                    axios.post(`/activities/`, {
                        appropriation: appr_id,
                        status: this.act.status,
                        activity_type: this.act.activity_type,
                        id: this.act.id,
                        start_date: this.act.start_date,
                        end_date: this.act.end_date,
                        service: this.act.service
                    })
                    .then(res => {
                        this.$router.push(`/appropriation/${ appr_id }`)
                    })
                    .catch(err => console.log(err))
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

    .activity-edit {
        margin: 0;
    }

    .activity-edit .cancel-btn {
        margin-left: 0.5rem;
        background-color: transparent;
        color: var(--primary);
        border-color: transparent;
    }

</style>