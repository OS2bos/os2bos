<template>

    <div class="assessment">
    
        <h2 v-if="!create_mode">Opdatér vurdering</h2>
        <h2 v-else>Vurdering</h2>

        <fieldset>
            <label for="selectField1">Indsatstrappen</label>
            <select id="selectField1" v-model="cas.effort_step" required @change="updateEffort()">
                <option value="STEP_ONE">Trin 1 - Tidlig indsats i almenområdet</option>
                <option value="STEP_TWO">Trin 2 - Forebyggelse</option>
                <option value="STEP_THREE">Trin 3 - Hjemmebaserede indsatser</option>
                <option value="STEP_FOUR">Trin 4 - Anbringelse i slægt eller netværk</option>
                <option value="STEP_FIVE">Trin 5 - Anbringelse i forskellige typer af plejefamilier</option>
                <option value="STEP_SIX">Trin 6 - Anbringelse i institutionstilbud</option>
            </select>
        </fieldset>

        <fieldset>
            <label for="selectField2">Skaleringstrappen</label>
            <select id="selectField2" v-model="cas.scaling_step" required @change="updateScaling()">
                <option value="10">10</option>
                <option value="9">9</option>
                <option value="8">8</option>
                <option value="7">7</option>
                <option value="6">6</option>
                <option value="5">5</option>
                <option value="4">4</option>
                <option value="3">3</option>
                <option value="2">2</option>
                <option value="1">1</option>
            </select>
        </fieldset>

        <fieldset v-if="!create_mode">
            <label for="textArea">Bemærkning</label>
            <textarea id="textArea" v-model="cas.history_change_reason" @change="updateNote()"></textarea>
        </fieldset>

    </div>

</template>

<script>

    import axios from '../http/Http.js'

    export default {

        props: [
            'caseObj'
        ],
        data: function() {
            return {
                cas: {
                    effort_step: null,
                    scaling_step: null,
                    history_change_reason: null
                },
                create_mode: false
            }
        },
        methods: {
            updateEffort: function() {
                this.$emit('assessment', {
                    effort_step: this.cas.effort_step
                })
            },
            updateScaling: function() {
                this.$emit('assessment', {
                    scaling_step: this.cas.scaling_step
                })
            },
            updateNote: function() {
                this.$emit('assessment', {
                    history_change_reason: this.cas.history_change_reason
                })
            }
        },
        created: function() {
            if (this.caseObj.id) {
                this.cas = this.caseObj
            } else {
                this.create_mode = true
            }
        }
    }
    
</script>

<style>

    .assessment {
        margin: 0;
    }

    .assessment-form {
        padding: 0;
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