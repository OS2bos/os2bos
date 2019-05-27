<template>

    <article class="appropriation-edit">
        <h1 v-if="appr_data.sbsys_id === ''">Ny bevillingskrivelse</h1>
        <form @submit.prevent="saveAppr(appr_data)">
            <fieldset>
                <label for="field-sbsysid">SBSYS-sag</label>
                <input id="field-sbsysid" type="text" :value="appr_data.sbsys_id">
            </fieldset>
            <fieldset>
                <label for="field-lawref">Bevilling efter §</label>
                <select :value="appr_data.law_ref" id="field-lawref">
                    <option val="SEL §45 Ledsagerordning 12">SEL §45 Ledsagerordning 12</option>
                    <option vale="SEL §52.3.7 Anbringelse udenfor hjemmet">SEL §52.3.7 Anbringelse udenfor hjemmet</option>
                </select>
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
            'appropriationData'
        ],
        data: function() {
            return {
                appr_data: {
                    sbsys_id: '',
                    law_ref: ''
                }
            }
        },
        methods: {
            saveAppr: function(data) {
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
            if (this.appropriationData) {
                this.appr_data = this.appropriationData
            }
        }
    }
    
</script>

<style>

    .appropriation-edit {
        margin: 0;
    }

    .appropriation-edit .cancel-btn {
        margin-left: 0.5rem;
        background-color: transparent;
        color: var(--primary);
        border-color: transparent;
    }

</style>
