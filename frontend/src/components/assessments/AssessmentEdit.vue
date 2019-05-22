<template>
    <article class="assessment">
        <form>
            <fieldset>
                <label for="inputSearch">SBSYS Hovedsag:</label>
                <input id="inputSearch" type="search" v-model="cas.sbsys_id">
                <button class="assessment-button">Hent</button>
            </fieldset>
        </form>

        <div>
            <form id="getForm" @submit.prevent="saveAssessment(assessment_data)">
                <fieldset>
                    <h3>Sagspart:</h3>
                    <dl>
                        <dt>CPR-nr:</dt>
                        <dd>{{ cas.cpr_no }}</dd>
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
                        <option>{{ cas.scaling_staircase }}</option>
                        <option>5</option>
                    </select>
                </fieldset>

                <fieldset>
                    <label for="textArea">Bemærkning:</label>
                    <textarea id="textArea" v-model="assessment_data.note"></textarea>
                </fieldset>

                <fieldset>
                    <input type="submit" value="Opdater">
                    <button class="cancel-btn" type="reset" @click="cancelEdit()">Annullér</button>
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
            'assessmentData'
        ],
        data: function() {
            return {
                cas: null,
                assessment_data: {
                    note: ''
                }
            }
        },
        methods: {
            update: function() {
                this.fetchCase(this.$route.params.id)
            },
            fetchCase: function(id) {
                axios.get('../../case-data.json')
                .then(res => {
                    this.cas = res.data[0]
                })
                .catch(err => console.log(err))
            },
            saveAssessment: function(data) {
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
            this.update()
        }
    }
    
</script>

<style>

    .assessment {
        margin: 0;
    }

    .assessment-button {
        margin-left: 1rem;
    }

    .assessment .cancel-btn {
      background-color: transparent;
      color: var(--primary);
      border-color: transparent;
    }

</style>