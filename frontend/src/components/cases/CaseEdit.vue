<template>
    <section class="case">
        <form @submit.prevent="saveChanges()">
            <h1>Tilknyt/Redigér hovedsag</h1>
            
            <fieldset>
                <label for="field-sbsys-id">SBSYS Hovedsag:</label>
                <input id="field-sbsys-id" type="search" v-model="cas.sbsys_id">
                <button class="case-button" disabled>Hent</button>
            </fieldset>
        
            <fieldset>
                <label for="field-name">Sagspart, navn</label>
                <input id="field-name" type="text" v-model="cas.name">
            </fieldset>

            <fieldset>
                <label for="field-cpr">Sagspart, CPR-nr</label>
                <input id="field-cpr" type="text" v-model="cas.cpr_number">
            </fieldset>

            <fieldset>
                <h3>Familie og relationer:</h3>
                <dl>
                    <dt>Mor:</dt>
                    <dd>ikke implementeret</dd>
                    <dt>Far:</dt>
                    <dd>ikke implementeret</dd>
                    <dt>Andre:</dt>
                    <dd>ikke implementeret</dd>
                </dl>
            </fieldset>

            <fieldset>
                <h3>Kommune:</h3>
                <label for="selectField1">Betalingskommune:</label>
                <list-picker :dom-id="'selectField1'" :selected-id="cas.paying_municipality" @selection="changeMuni($event, 'paying_municipality')" :list="municipalities" />
            </fieldset>

            <fieldset>
                <label for="selectField2">Handlekommune:</label>
                <list-picker :dom-id="'selectField2'" :selected-id="cas.acting_municipality" @selection="changeMuni($event, 'acting_municipality')" :list="municipalities" />
            </fieldset>

            <fieldset>
                <label for="selectField3">Bopælsskommune:</label>
                <list-picker :dom-id="'selectField3'" :selected-id="cas.residence_municipality" @selection="changeMuni($event, 'residence_municipality')" :list="municipalities" />
            </fieldset>

            <fieldset>
                <h3>Målgruppe:</h3>
                <input id="inputRadio1" type="radio" name="radioButtonSet">
                <label for="inputRadio1">Familieafdelingen</label>
                <input id="inputRadio2" type="radio" name="radioButtonSet">
                <label for="inputRadio2">Handicapafdelingen</label>
            </fieldset>

            <fieldset>
                <h3>Andet:</h3>
                <input id="inputCheckbox1" type="checkbox" name="radioButtonSet">
                <label for="inputCheckbox1">Integrationsindsatsen</label>
                <input id="inputCheckbox2" type="checkbox" name="radioButtonSet">
                <label for="inputCheckbox2">Tværgående ungeindsats</label>
            </fieldset>

            <fieldset>
                <label for="selectField">Oprindeligt distrikt:</label>
                <select id="selectField">
                    <option>{{ cas.original_district}}</option>
                </select>
            </fieldset>

            <fieldset>
                <dt>Indsatstrappen:</dt>
                <dd>{{ cas.effort_stairs }}</dd>
                <dt>Skaleringstrappe:</dt>
                <dd>{{ cas.scaling_staircase }}</dd>
            </fieldset>

            <fieldset>
                <button @click="$router.push(`/assessment/${ cas.id }`)">Vurdering</button>
            </fieldset>

            <fieldset>
                <h3>Sagsbehandling:</h3>
                <dl>
                    <dt>Sagsbehander:</dt>
                    <dd>{{ cas.case_worker }}</dd>
                    <dt>Team:</dt>
                    <dd>ikke implementeret</dd>
                </dl>
                <fieldset>
                <label for="selectField">Distrikt:</label>
                <select id="selectField">
                    <option>{{ cas.district }}</option>
                </select>
                </fieldset>
                <fieldset>
                    <dt>Leder:</dt>
                    <dd>ikke implementeret</dd>
                </fieldset>
            </fieldset>
            
            <fieldset>
                <input type="submit" value="Gem">
                <button class="cancel-btn" type="cancel">Annullér</button>
            </fieldset>
            
        </form>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import ListPicker from '../forms/ListPicker.vue'

    export default {

        components: {
            ListPicker
        },
        props: [
            'caseObj'
        ],
        data: function() {
            return {
                item: null,
                cas: {},
                create_mode: true
            }
        },
        computed: {
            municipalities: function() {
                return this.$store.getters.getMunis
            }
        },
        methods: {
            changeMuni: function(ev, type) {
                this.cas[type] = ev
            },
            saveChanges: function() {
                if (!this.create_mode) {
                    axios.patch(`/cases/${ this.cas.id }/`, {
                        name: this.cas.name,
                        cpr_number: this.cas.cpr_number,
                        paying_municipality: this.cas.paying_municipality,
                        acting_municipality: this.cas.acting_municipality,
                        residence_municipality: this.cas.residence_municipality
                    })
                    .then(res => {
                        this.$emit('save', res.data)
                    })
                    .catch(err => console.log(err))
                } else {
                    axios.post(`/cases/`, {
                        sbsys_id: this.cas.sbsys_id,
                        name: this.cas.name,
                        cpr_number: this.cas.cpr_number
                    })
                    .then(res => {
                        this.$router.push('/')
                    })
                    .catch(err => console.log(err))
                }
            }
        },
        created: function() {
            if (this.caseObj) {
                this.create_mode = false
                this.cas = this.caseObj
            }
        }
    }
    
</script>

<style>

    .case {
        margin: 1rem;
    }

    .case-button {
        margin-left: 1rem;
    }

    .case .cancel-btn {
        margin-left: 0.5rem;
        background-color: transparent;
        color: var(--primary);
        border-color: transparent;
    }

</style>