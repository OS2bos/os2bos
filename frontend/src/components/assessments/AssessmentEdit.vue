<template>
    <article class="assessment">
        <form>
            <fieldset>
                <label for="inputSearch">SBSYS Hovedsag:</label>
                <input id="inputSearch" type="search" v-model="cas.sbsys_id">
                <button class="assessment-button" disabled>Hent</button>
            </fieldset>
        </form>

        <div>
            <form id="getForm" @submit.prevent="saveChanges()">
                <fieldset>
                    <h3>Sagspart:</h3>
                    <dl>
                        <dt>CPR-nr:</dt>
                        <dd>{{ cas.cpr_number }}</dd>
                        <dt>Navn:</dt>
                        <dd>{{ cas.name }}</dd>
                    </dl>
                </fieldset>

                <fieldset>
                    <label for="selectField1">Indsatstrappen:</label>
                    <select id="selectField1" v-model="cas.effort_stairs">
                        <option value="Trin 1 - Tidlig indsats i almenområdet">Trin 1 - Tidlig indsats i almenområdet</option>
                        <option value="Trin 2 - Forebyggelse">Trin 2 - Forebyggelse</option>
                        <option value="Trin 3 - Hjemmebaserede indsatser">Trin 3 - Hjemmebaserede indsatser</option>
                        <option value="Trin 4 - Anbringelse i slægt eller netværk">Trin 4 - Anbringelse i slægt eller netværk</option>
                        <option value="Trin 5 - Anbringelse i forskellige typer af plejefamilier">Trin 5 - Anbringelse i forskellige typer af plejefamilier</option>
                        <option value="Trin 6 - Anbringelse i institutionstilbud">Trin 6 - Anbringelse i institutionstilbud</option>
                    </select>
                </fieldset>
                <fieldset>
                    <label for="selectField2">Skaleringstrappe:</label>
                    <select id="selectField2" v-model="cas.scaling_staircase">
                        <option>1</option>
                        <option>2</option>
                        <option>3</option>
                        <option>4</option>
                        <option>5</option>
                        <option>6</option>
                    </select>
                </fieldset>

                <fieldset>
                    <label for="textArea">Bemærkning:</label>
                    <textarea id="textArea" v-model="cas.note"></textarea>
                </fieldset>

                <fieldset>
                    <input type="submit" value="Opdater">
                    <button class="cancel-btn" type="cancel">Annullér</button>
                </fieldset>
            </form>
        </div>
    </article>

</template>

<script>

    import History from './History.vue'
    import axios from '../http/Http.js'

    export default {

        components: {
            History
        },

        props: [
            'assessmentObj'
        ],
        data: function() {
            return {
                cas: null,
                create_mode: true
            }
        },
        methods: {
           saveChanges: function() {
                if (!this.create_mode) {
                    axios.patch(`/cases/${ this.cas.id }/`, {
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
            if (this.assessmentObj) {
                this.create_mode = false
                this.cas = this.assessmentObj
            }
        }
    }
    
</script>

<style>

    .assessment {
        margin: 0;
    }

    .assessment-button {
        margin-left: 0.5rem;
    }

    .assessment .cancel-btn {
        margin-left: 0.5rem;
        background-color: transparent;
        color: var(--primary);
        border-color: transparent;
    }

</style>