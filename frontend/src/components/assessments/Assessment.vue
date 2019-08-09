<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <div class="assessment" v-if="cas">
        <header class="assessment-header">
            <h1>Vurderinger af {{ cas.cpr_number }}, {{ cas.name }}</h1>
        </header>

        <form class="assessment-form" @submit.prevent="saveAssessment()">
            <div class="row">
                <div class="column">
                    <assessment-edit :case-obj="cas" @assessment="updateAssessment" />
                    <fieldset style="margin: 0 1rem 1rem;">
                        <input :disabled="disableButton" type="submit" value="Opdatér">
                        <button class="cancel-btn" type="button" @click="cancel()">Annullér</button>
                    </fieldset>

                </div>
                <div class="column"></div>
            </div>
        </form>

        <assessment-history :case-obj="cas" />
    </div>

</template>

<script>

    import AssessmentEdit from './AssessmentEdit.vue'
    import AssessmentHistory from './AssessmentHistory.vue'
    import axios from '../http/Http.js'

    export default {

        components: {
            AssessmentHistory,
            AssessmentEdit
        },

        data: function() {
            return {
                cas_id: null,
                cas: null,
                disableButton: true
            }
        },
        methods: {
            update: function() {
                this.cas_id = this.$route.params.id
                this.fetchCase(this.cas_id)
            },
            fetchCase: function(id) {
                axios.get(`/cases/${ this.cas_id}/`)
                .then(res => {
                    this.cas = res.data
                    this.$store.commit('setBreadcrumb', [
                        {
                            link: '/',
                            title: 'Mine sager'
                        },
                        {
                            link: `/case/${ this.cas.id }/`,
                            title: `Sag ${ this.cas.sbsys_id }`
                        },
                        {
                            title: `Vurderinger`
                        }
                    ])
                })
                .catch(err => console.log(err))
            },
            updateAssessment: function(assessment) {
                if (assessment.scaling_step) {
                    this.cas.scaling_step = assessment.scaling_step
                }
                if (assessment.effort_step) {
                    this.cas.effort_step = assessment.effort_step
                }
                if (assessment.history_change_reason) {
                    this.cas.history_change_reason = assessment.history_change_reason
                }
                this.disableButton = false
            },
            saveAssessment: function() {
                axios.patch(`/cases/${ this.cas_id}/`, {
                    scaling_step: this.cas.scaling_step,
                    effort_step: this.cas.effort_step,
                    history_change_reason: this.cas.history_change_reason
                })
                .then(res => {
                    this.update()
                    this.disableButton = true
                })
                .catch(err => console.log(err))
            },
            cancel: function() {
                this.$emit('close')
                this.$router.push(`/case/${ this.$route.params.id }/`)
            }
        },
        created: function() {
            this.update()
        }
    }
    
</script>

<style>

    .assessment {
        margin: 1rem;
    }

    .assessment-form {
        margin-bottom: 2rem;
    }

</style>