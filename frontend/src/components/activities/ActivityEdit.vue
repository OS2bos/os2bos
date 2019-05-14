<template>

    <article class="activity-edit">
        <h1 v-if="act_data.sbsys_id === ''">Ny akvititet</h1>
        <form @submit.prevent="saveAct(act_data)">
            <fieldset>
                <legend>Status</legend>
                <input type="radio" id="field-status-true" :value="false" v-model="act_data.is_estimated_cost">
                <label for="field-status-true">Bevilling</label>
                <input type="radio" id="field-status-false" :value="true" v-model="act_data.is_estimated_cost">
                <label for="field-status-false">Forventning</label>
            </fieldset>
            <fieldset>
                <legend>Type</legend>
                <input type="radio" id="field-type-true" :value="true" v-model="act_data.is_main_act">
                <label for="field-type-true">Hovedudgift</label>
                <input type="radio" id="field-type-false" :value="false" v-model="act_data.is_main_act">
                <label for="field-type-false">Tillægsudgift</label>
            </fieldset>
            <fieldset>
                <label for="field-lawref">Bevilling efter §</label>
                <select v-model="act_data.law_ref" id="field-lawref">
                    <option value="SEL §45 Ledsagerordning 12">SEL §45 Ledsagerordning 12</option>
                    <option value="SEL §52.3.7 Anbringelse udenfor hjemmet">SEL §52.3.7 Anbringelse udenfor hjemmet</option>
                </select>
            </fieldset>
            <fieldset>
                <label>Aktivitet</label>
                <select v-model="act_data.activity">
                    <option value="Plejefamilier eksl. vederlag">Plejefamilier eksl. vederlag</option>
                    <option value="Kørsel">Kørsel</option>
                    <option value="Kost- og efterskoler">Kost- og efterskoler</option>
                </select>
            </fieldset>
            <fieldset>
                <label for="field-startdate">Startdato</label>
                <input type="date" id="field-startdate">
            </fieldset>
            <fieldset>
                <label for="field-enddate">Slutdato</label>
                <input type="date" id="field-enddate">
            </fieldset>
            <hr>
            <fieldset>
                <label for="field-cost">Bevilget beløb</label>
                <input type="number" id="field-cost" v-model="act_data.payment.amount">
            </fieldset>
            <fieldset>
                <legend>Udgiftstype</legend>
                <input type="radio" id="field-cost-single" :value="false" v-model="act_data.is_single_payment">
                <label for="field-cost-single">Følgeydelse</label>
                <input type="radio" id="field-cost-recurring" :value="true" v-model="act_data.is_single_payment">
                <label for="field-cost-recurring">Enkeltudgift</label>
            </fieldset>
            <fieldset>
                <label for="field-note">Bemærkning</label>
                <textarea v-model="act_data.payment.note" id="field-note"></textarea>
            </fieldset>
            <hr>
            <fieldset>
                <legend>Betalingsmodtager</legend>
                <input type="radio" id="field-payment-type-inherit" value="inherit" v-model="act_data.payment.payee.type">
                <label for="field-payment-type-inherit">Samme som hovedydelsen</label>
                <input type="radio" id="field-payment-type-intern" value="intern" v-model="act_data.payment.payee.type">
                <label for="field-payment-type-intern">Intern</label>
                <input type="radio" id="field-payment-type-person" value="person" v-model="act_data.payment.payee.type">
                <label for="field-payment-type-person">Person</label>
                <input type="radio" id="field-payment-type-firm" value="firma" v-model="act_data.payment.payee.type">
                <label for="field-payment-type-firm">Firma</label>
            </fieldset>
            <template v-if="act_data.payment.payee.type !== 'inherit'">
                <fieldset>
                    <label for="field-payment-id">
                        <template v-if="act_data.payment.payee.type === 'person'">CPR-nr</template>
                        <template v-if="act_data.payment.payee.type === 'firma'">CVR-nr</template>
                        <template v-if="act_data.payment.payee.type === 'intern'">Reference</template>
                    </label>
                    <input type="text" id="field-payment-id" v-model="act_data.payment.payee.id">
                </fieldset>
                <fieldset>
                    <label for="field-payment-name">Navn</label>
                    <input type="text" id="field-payment-name" v-model="act_data.payment.payee.name">
                </fieldset>
                <fieldset>
                    <legend>Betalingsmåde</legend>
                    <input type="radio" id="field-payment-method-cash" value="kontant" v-model="act_data.payment.method.type">
                    <label for="field-payment-method-cash">Kontant udbetaling</label>
                    <input type="radio" id="field-payment-method-sd" value="SD-løn" v-model="act_data.payment.method.type">
                    <label for="field-payment-method-sd">SD-løn</label>
                    <input type="radio" id="field-payment-method-invoice" value="faktura" v-model="act_data.payment.method.type">
                    <label for="field-payment-method-invoice">Faktura</label>
                    <input type="radio" id="field-payment-method-internal" value="intern afregning" v-model="act_data.payment.method.type">
                    <label for="field-payment-method-internal">Intern afregning</label>
                </fieldset>
            </template>
            <hr>
            <fieldset>
                <input type="submit" value="Gem">
                <button class="cancel-btn" type="reset" @click="cancelEdit()">Annullér</button>
            </fieldset>
        </form>
    </article>

</template>

<script>

    import axios from '../http/Http.js'

    export default {

        props: [
            'activityData'
        ],
        data: function() {
            return {
                act_data: {
                    is_estimated_cost: false
                }
            }
        },
        methods: {
            saveAct: function(data) {
                axios.patch('/', data)
                .then(res => {
                    this.$emit('saved', res.data)
                })
                .catch(err => console.log(err))
                
            },
            cancelEdit: function() {
                this.$emit('cancelled')
            }
        },
        created: function() {
            if (this.activityData) {
                this.act_data = this.activityData
            }
        }
    }
    
</script>

<style>

    .activity-edit {
        margin: 0;
    }

    .activity-edit .cancel-btn {
        background-color: transparent;
        color: var(--primary);
        border-color: transparent;
    }

</style>