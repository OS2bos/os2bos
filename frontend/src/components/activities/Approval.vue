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
                            <h1>Godkend ydelser</h1>
                        </slot>
                    </div>

                    <ul>
                        <li v-for="act in act_list" :key="act.id">
                            <span v-html="displayStatus(act.status)"></span> 
                            {{ activityId2name(act.details) }} - {{ act.total_cost_this_year }} kr<br>
                            {{ displayDate(act.start_date) }} - {{ displayDate(act.end_date) }}
                        </li>
                    </ul>

                    <div class="modal-body">
                        <slot name="body">
                            <h3>Bevilling foretaget på følgende niveau</h3>
                            <fieldset>
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
                                <error />
                            </fieldset>

                            <fieldset>
                                <label for="field-text">Evt. bemærkning</label>
                                <textarea id="field-text" v-model="appr.approval_note"></textarea>
                            </fieldset>
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
            saveChanges: function() {
                let approvable_acts = []
                for (let a of this.act_list) {
                    approvable_acts.push(a.id)
                }
                let data = {
                    approval_level: this.appr.approval_level,
                    approval_note: this.appr.approval_note,
                    list_of_acts: approvable_acts
                }
                axios.patch(`/appropriations/${ this.apprId }/grant/`, data)
                .then(() => {
                    notify('Bevilling godkendt', 'success')
                    this.$store.dispatch('fetchActivities', this.apprId)
                    this.$emit('close')
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
        max-width: 90vw;
        max-height: 90vh;
        overflow-x: hidden;
        overflow-y: auto;
    }

</style>
