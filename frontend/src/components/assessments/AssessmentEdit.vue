<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <div class="assessment">
    
        <h2 v-if="!create_mode && requiredScalingStep === true || requiredEffortStep === true">Opdatér vurdering</h2>

        <fieldset>
            <legend>Vurdering:</legend>
            <p v-if="requiredScalingStep === false && requiredEffortStep === false">Den valgte målgruppe giver ikke mulighed for at vælge vurdering.</p>

            <template v-if="requiredEffortStep === true">
                <label class="required" for="field-indsatstrappe">Indsatstrappen</label>
                <select id="field-indsatstrappe" v-model="cas.effort_step" @change="updateEffort()" required>
                    <option v-for="e in effort_steps" :value="e.id" :key="e.id">
                        <span v-if="e.active === false">(</span>
                        {{ e.name }}
                        <span v-if="e.active === false">)</span>
                    </option>
                </select>
                <error err-key="effort_step" />
            </template>
        
            <template v-if="requiredScalingStep === true">
                <label class="required" for="field-skaleringstrappe">Skaleringstrappen</label>
                <select id="field-skaleringstrappe" v-model="cas.scaling_step" @change="updateScaling()" required>
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
                <error err-key="scaling_step" />
            </template>
        
            <template v-if="requiredScalingStep === true || requiredEffortStep === true">
                <label for="textArea">Supplerende information til vurdering</label>
                <textarea maxlength="100" id="textArea" v-model="cas.assessment_comment" @change="updateNote()"></textarea>
            </template>
        </fieldset>

    </div>

</template>

<script>

    import axios from '../http/Http.js'
    import Error from '../forms/Error.vue'

    export default {

        components: {
            Error
        },
        props: [
            'caseObj'
        ],
        data: function() {
            return {
                cas: {
                    effort_step: null,
                    scaling_step: null,
                    assessment_comment: null
                },
                create_mode: false,
            }
        },
        computed: {
            effort_steps: function() {
                return this.$store.getters.getEffortSteps
            },
            targetGroups: function() {
                return this.$store.getters.getTargetGroups
            },
            requiredEffortStep: function() {
                if (this.caseObj.target_group) {
                    let target = this.targetGroups.filter(tar => tar.id === this.caseObj.target_group)
                    return target[0].required_fields_for_case.filter(tar => tar === 'effort_step').length === 1
                } else {
                    return false
                }
            },
            requiredScalingStep: function() {
                if (this.caseObj.target_group) {
                    let target = this.targetGroups.filter(tar => tar.id === this.caseObj.target_group)
                    return target[0].required_fields_for_case.filter(tar => tar === 'scaling_step').length === 1
                } else {
                    return false
                }
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
                    assessment_comment: this.cas.assessment_comment
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