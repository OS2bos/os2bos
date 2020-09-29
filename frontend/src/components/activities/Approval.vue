<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <form @submit.prevent="saveChanges" class="approval modal-form">
        <modal-dialog @closedialog="closeDiag">
            
            <h2 slot="header" style="padding: 0;">Godkend ydelser</h2>

            <div slot="body">
                <warning :content="warning" />
                <warning :content="payDateRule" />

                <table>
                    <thead>
                        <tr>
                            <th></th>
                            <th>Ydelse</th>
                            <th>Periode</th>
                            <th class="right">Udgift i år</th>
                            <th class="right">Udgift, årligt</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-if="main_act_list.length > 0">
                            <th colspan="5">Hovedydelse</th>
                        </tr>
                        <tr v-for="act in main_act_list" :key="act.id">
                            <td><span v-html="displayStatus(act.status)"></span> </td>
                            <td v-html="activityId2name(act.details)"></td>
                            <td>{{ displayDate(act.start_date) }} - {{ displayDate(act.end_date) }}</td>
                            <td class="right">{{ displayDigits(act.total_cost_this_year) }} kr</td>
                            <td class="right">{{ displayDigits(act.total_cost_full_year) }} kr</td>
                        </tr>
                        <tr v-if="suppl_act_list.length > 0">
                            <th colspan="5">Følgeydelser</th>
                        </tr>
                        <tr v-for="act in suppl_act_list" :key="act.id">
                            <td><span v-html="displayStatus(act.status)"></span> </td>
                            <td v-html="activityId2name(act.details)"></td>
                            <td>{{ displayDate(act.start_date) }} - {{ displayDate(act.end_date) }}</td>
                            <td class="right">{{ displayDigits(act.total_cost_this_year) }} kr</td>
                            <td class="right">{{ displayDigits(act.total_cost_full_year) }} kr</td>
                        </tr>
                    </tbody>
                </table>

                <error />

                <div class="row">
                    <div style="width: 50%;">
                        <fieldset style="display: block;">
                            <legend style="margin-bottom: .75rem">Bevilling foretaget på følgende niveau</legend>
                            <div v-for="appro_lvl in approval_level_list" :key="appro_lvl.id">
                                <input 
                                    :id="`radio-btn-${ appro_lvl.id }`" 
                                    type="radio" 
                                    :value="appro_lvl.id" 
                                    v-model="appr.approval_level" 
                                    name="approval-group"
                                    required>
                                <label 
                                    :for="`radio-btn-${ appro_lvl.id }`"
                                    style="text-transform: capitalize;">
                                    <span v-if="appro_lvl.active === true">{{ appro_lvl.name }}</span>
                                    <strong v-if="appro_lvl.active === false">{{ appro_lvl.name }}</strong>
                                </label>
                            </div>
                        </fieldset>
                    </div>
                    <div style="width: 50%;">
                        <fieldset style="margin-top: .25rem; display: block;">
                            <label for="field-text">Evt. bemærkning</label>
                            <textarea id="field-text" v-model="appr.approval_note" style="height: 14rem;"></textarea>
                        </fieldset>
                    </div>
                </div>
            </div>
            
            <div slot="footer">
                <button type="submit">Godkend</button>
                <button type="button" @click="closeDiag">Annullér</button>
            </div>

        </modal-dialog>
    </form>
</template>

<script>

    import axios from '../http/Http.js'
    import notify from '../notifications/Notify.js'
    import Error from '../forms/Error.vue'
    import { activityId2name, displayStatus } from '../filters/Labels.js'
    import { cost2da } from '../filters/Numbers.js'
    import { json2jsDate } from '../filters/Date.js'
    import Warning from '../warnings/Warning.vue'
    import { checkRulePayDate } from '../filters/Rules.js'
    import ModalDialog from '../dialog/Dialog.vue'

    export default {

        components: {
            Error,
            Warning,
            ModalDialog
        },
        props: [
            'acts',
            'apprId',
            'warning'
        ],
        data: function() {
            return {
                appr: {}
            }
        },
        computed: {
            act_list: function() {
                return this.acts
            },
            main_act_list: function() {
                return this.acts.filter(function(a) {
                    return a.activity_type === 'MAIN_ACTIVITY'
                })
            },
            suppl_act_list: function() {
                return this.acts.filter(function(a) {
                    return a.activity_type === 'SUPPL_ACTIVITY'
                })
            },
            approval_level_list: function() {
                return this.$store.getters.getApprovals
            },
            payDateRule: function() {
                let rule = false
                let rule_breakers = this.act_list.filter(act => {
                    const rulecheck = checkRulePayDate(act.start_date, act.payment_plan.payment_method)
                    if (rulecheck) {
                        rule = rulecheck
                        return true
                    } else {
                        return false
                    }
                })
                return rule
            }
        },
        methods: {
            displayStatus: function(status) {
                return displayStatus(status)
            },
            activityId2name: function(id) {
                return activityId2name(id)
            },
            displayDate: function(dt) {
                return json2jsDate(dt)
            },
            displayDigits: function(num) {
                return cost2da(num)
            },
            closeDiag: function() {
                this.$emit('close')
            },
            saveChanges: function() {
                let approvable_acts = []
                for (let a of this.act_list) {
                    approvable_acts.push(a.id)
                }
                let data = {
                    approval_level: this.appr.approval_level,
                    approval_note: this.appr.approval_note,
                    activities: approvable_acts
                }
                axios.patch(`/appropriations/${ this.apprId }/grant/`, data)
                .then(() => {
                    this.$store.dispatch('fetchActivities', this.apprId)
                    this.$store.dispatch('fetchAppropriation', this.apprId)
                    this.closeDiag()
                    notify('Bevillingsskrivelse er godkendt', 'success')
                    notify('Bevillingsskrivelsen vil blive journaliseret i SBSYS')
                    for (let a in this.act_list) {
                        notify(`Der er givet besked til administrationen om din ændring af ${ this.act_list[a].details__name }`)
                    }
                    
                })
                .catch(err => {
                    this.$store.dispatch('parseErrorOutput', err)
                })
            }
        }
    }
    
</script>

<style>

    .approval .modal-container {
        max-width: 95vw;
        max-height: 95vh;
    }

    .approval .modal-body {
        overflow-x: hidden;
        overflow-y: auto;
    }

    .approval .modal-footer {
        box-shadow: 0 -.25rem 1rem hsla(var(--color1), 83%, 62%, .125);
        padding: 2rem;
        margin: 0 -2rem -2rem;
    }

</style>
