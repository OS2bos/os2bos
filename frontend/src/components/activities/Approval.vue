<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <form @submit.prevent="saveChanges()" class="approval modal-form">
        <div class="modal-mask">
            <div class="modal-wrapper">
                <div class="modal-container">

                    <div class="modal-header">
                        <slot name="header">
                            <h2>Godkend ydelser</h2>
                        </slot>
                    </div>

                    <div class="modal-body">
                        <slot name="body">

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
                                        <td>{{ activityId2name(act.details) }}</td>
                                        <td>{{ displayDate(act.start_date) }} - {{ displayDate(act.end_date) }}</td>
                                        <td class="right">{{ displayDigits(act.total_cost_this_year) }} kr</td>
                                        <td class="right">{{ displayDigits(act.total_cost_full_year) }} kr</td>
                                    </tr>
                                    <tr v-if="suppl_act_list.length > 0">
                                        <th colspan="5">Følgeydelser</th>
                                    </tr>
                                    <tr v-for="act in suppl_act_list" :key="act.id">
                                        <td><span v-html="displayStatus(act.status)"></span> </td>
                                        <td>{{ activityId2name(act.details) }}</td>
                                        <td>{{ displayDate(act.start_date) }} - {{ displayDate(act.end_date) }}</td>
                                        <td class="right">{{ displayDigits(act.total_cost_this_year) }} kr</td>
                                        <td class="right">{{ displayDigits(act.total_cost_full_year) }} kr</td>
                                    </tr>
                                </tbody>
                            </table>

                            <error />

                            <div class="row">
                                <div style="width: 50%; padding-top: 1rem;">
                                    <fieldset style="padding-right: 1rem;">
                                        <legend>Bevilling foretaget på følgende niveau</legend>
                                        <input id="inputRadio1" type="radio" value="5" v-model="appr.approval_level" name="approval-group" required>
                                        <label for="inputRadio1">Afsnitsleder</label>
                                        <input id="inputRadio2" type="radio" value="1" v-model="appr.approval_level" name="approval-group" required>
                                        <label for="inputRadio2">Egenkompetence</label>
                                        <input id="inputRadio3" type="radio" value="3" v-model="appr.approval_level" name="approval-group" required>
                                        <label for="inputRadio3">Fagspecialist</label>
                                        <input id="inputRadio4" type="radio" value="4" v-model="appr.approval_level" name="approval-group" required>
                                        <label for="inputRadio4">Teamleder</label>
                                        <input id="inputRadio5" type="radio" value="2" v-model="appr.approval_level" name="approval-group" required>
                                        <label for="inputRadio5">Teammøde</label>
                                        <input id="inputRadio6" type="radio" value="6" v-model="appr.approval_level" name="approval-group" required>
                                        <label for="inputRadio6">Ungdomskriminalitetsnævnet</label>
                                    </fieldset>
                                </div>
                                <div style="width: 50%;">
                                    <fieldset style="padding-left: 1rem; ">
                                        <label for="field-text">Evt. bemærkning</label>
                                        <textarea id="field-text" v-model="appr.approval_note" style="height: 14rem;"></textarea>
                                    </fieldset>
                                </div>
                            </div>

                        </slot>
                    </div>

                    <div class="modal-footer">
                        <slot name="footer">
                            <button type="button" class="modal-cancel-btn" @click="$emit('close')">Annullér</button>
                            <button class="modal-confirm-btn" type="submit">Godkend</button>
                        </slot>
                    </div>
                </div>
            </div>
        </div>
    </form>
</template>

<script>

    import axios from '../http/Http.js'
    import notify from '../notifications/Notify.js'
    import Error from '../forms/Error.vue'
    import { activityId2name, displayStatus } from '../filters/Labels.js'
    import { cost2da } from '../filters/Numbers.js'
    import { json2jsDate } from '../filters/Date.js'

    export default {

        components: {
            Error
        },
        props: [
            'acts',
            'apprId'
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
                    notify('Bevilling godkendt', 'success')
                    this.$store.dispatch('fetchActivities', this.apprId)
                    this.$store.dispatch('fetchAppropriation', this.apprId)
                    this.$emit('close')
                    this.$emit('approve')
                })
                .catch(err => {
                    this.$store.dispatch('parseErrorOutput', err)
                })
            }
        }
    }
    
</script>