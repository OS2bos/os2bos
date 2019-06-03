<template>

    <article class="activity-edit">
        <form @submit.prevent="saveChanges()">
        <h1>Opret/Redigér akvititet</h1>
            <fieldset>
                <legend>Status</legend>
                <input type="radio" id="field-status-true" :value="act.status === 'GRANTED'">
                <label for="field-status-true">Bevilling</label>
                <input type="radio" id="field-status-false" :value="act.status === 'EXPECTED'">
                <label for="field-status-false">Forventning</label>
            </fieldset>
            <fieldset>
                <legend>Type</legend>
                <input type="radio" id="field-type-true" :value="true">
                <label for="field-type-true">Hovedudgift</label>
                <input type="radio" id="field-type-false" :value="false">
                <label for="field-type-false">Tillægsudgift</label>
            </fieldset>
            <fieldset>
                <strong>Bevilling efter §</strong>
                <span>{{ act.activity_type }}</span>
            </fieldset>
            <fieldset>
                <label>Aktivitet</label>
                <select v-model="act.activity_type">
                    <option value="Plejefamilier eksl. vederlag">Plejefamilier eksl. vederlag</option>
                    <option value="Kørsel">Kørsel</option>
                    <option value="Ungeindsatsen">Ungeindsatsen</option>
                </select>
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
                <input type="number" id="field-cost">
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
                    <input type="text" id="field-payment-id">
                </fieldset>
                <fieldset>
                    <label for="field-payment-name">Navn</label>
                    <input type="text" id="field-payment-name" :value="act.user_created">
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
                <button class="cancel-btn" type="cancel">Annullér</button>
            </fieldset>
        </form>
    </article>

</template>

<script>

    import axios from '../http/Http.js'

    export default {

        props: [
            'activityObj'
        ],
        data: function() {
            return {
                act_data: {},
                act: {},
                create_mode: true
            }
        },
        methods: {
            saveChanges: function() {
                if (!this.create_mode) {
                    axios.patch(`/activities/${ this.activityObj.id }/`, {
                        id: this.activityObj.id
                    })
                    .then(res => {
                        this.$emit('save', res.data)
                    })
                    .catch(err => console.log(err))
                } else {
                    axios.post(`/activities/`, {
                        id: this.activityObj.id
                    })
                    .then(res => {
                        this.$router.push('/')
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