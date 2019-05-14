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
                <select :value="act_data.law_ref" id="field-lawref">
                    <option val="SEL §45 Ledsagerordning 12">SEL §45 Ledsagerordning 12</option>
                    <option vale="SEL §52.3.7 Anbringelse udenfor hjemmet">SEL §52.3.7 Anbringelse udenfor hjemmet</option>
                </select>
            </fieldset>
            <fieldset>
                <label>Aktivitet</label>
                <select :val="act_data.activity">
                    <option val="Plejefamilier eksl. vederlag">Plejefamilier eksl. vederlag</option>
                    <option val="Kørsel">Kørsel</option>
                    <option val="Kost- og efterskoler">Kost- og efterskoler</option>
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
