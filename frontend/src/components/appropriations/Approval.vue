<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <form @submit.prevent="saveChanges()" class="modal-form">
        <div class="modal-mask">
            <div class="modal-wrapper">
                <div class="modal-container">

                    <div class="modal-header">
                        <slot name="header">
                            <h1>Godkend bevilling</h1>
                        </slot>
                    </div>

                    <div class="modal-body">
                        <slot name="body">
                            <h3>Bevilling foretaget på følgende niveau</h3>
                            <fieldset>
                                <input id="inputRadio1" type="radio" value="5" v-model="appro.approval_level" name="approval-group" required>
                                <label for="inputRadio1">Afsnitsleder</label>
                                <input id="inputRadio2" type="radio" value="1" v-model="appro.approval_level" name="approval-group" required>
                                <label for="inputRadio2">Egenkompetence</label>
                                <input id="inputRadio3" type="radio" value="3" v-model="appro.approval_level" name="approval-group" required>
                                <label for="inputRadio3">Fagspecialist</label>
                                <input id="inputRadio4" type="radio" value="4" v-model="appro.approval_level" name="approval-group" required>
                                <label for="inputRadio4">Teamleder</label>
                                <input id="inputRadio5" type="radio" value="2" v-model="appro.approval_level" name="approval-group" required>
                                <label for="inputRadio5">Teammøde</label>
                                <input id="inputRadio6" type="radio" value="6" v-model="appro.approval_level" name="approval-group" required>
                                <label for="inputRadio6">Ungdomskriminalitetsnævnet</label>
                                <error />
                            </fieldset>

                            <fieldset>
                                <label for="field-text">Evt. bemærkning</label>
                                <textarea v-model="appro.approval_note"></textarea>
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

    export default {

        components: {
            Error
        },
        props: [
            'approvalObj'
        ],
        data: function() {
            return {
                appro: {}
            }
        },
        methods: {
            saveChanges: function() {
                let data = {
                    approval_level: this.appro.approval_level,
                    approval_note: this.appro.approval_note
                }
                axios.patch(`/appropriations/${ this.approvalObj.id }/grant/`, data)
                .then(() => {
                    notify('Bevilling godkendt', 'success')
                    this.$store.dispatch('fetchActivities', this.approvalObj.id)
                    this.$emit('close')
                })
                .catch(err => {
                    this.$store.dispatch('parseErrorOutput', err)
                })
            }
        },
        created: function() {
            if (this.approvalObj) {
                this.appro = this.approvalObj
            }
        }
       
    }
    
</script>
