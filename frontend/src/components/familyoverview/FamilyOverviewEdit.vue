<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <article class="familyoverview-edit">
        <header class="familyoverview-edit-header">
            <h1 v-if="create_mode">Opret relation</h1>
            <h1 v-else>Redigér relation</h1>
        </header>

        <!-- Delete relation modal -->
        <div v-if="showModal && !create_mode">
            <form @submit.prevent="deleteRelation()" class="modal-form">
                <div class="modal-mask">
                    <div class="modal-wrapper">
                        <div class="modal-container">

                            <div class="modal-header">
                                <slot name="header">
                                    <h2>Slet</h2>
                                </slot>
                            </div>

                            <div class="modal-body">
                                <slot name="body">
                                    <p>
                                        Er du sikker på, at du vil slette denne relation?
                                    </p>
                                </slot>
                            </div>

                            <div class="modal-footer">
                                <slot name="footer">
                                    <button type="button" class="modal-cancel-btn" @click="cancel()">Annullér</button>
                                    <button class="modal-delete-btn" type="submit">Slet</button>
                                </slot>
                            </div>
                        </div>
                    </div>
                </div>
            </form>
        </div>
        <form @submit.prevent="saveChanges()">

            <error />
            
            <fieldset>
                <cpr-lookup :cpr.sync="fam.cpr_number" :name.sync="fam.name" />
            </fieldset>
        
            <fieldset>
                <label class="required" for="field-relation">Relation</label>
                <input id="field-relation" type="text" v-model="fam.relation_type" required>
                <error err-key="relation_type" />
                <label for="field-sbsysid">Relateret SBSYS sag</label>
                <input id="field-sbsysid" type="text" v-model="fam.related_case">
            </fieldset>
                
            <fieldset class="form-actions">
                <input type="submit" value="Gem">
                <button v-if="!create_mode" type="button" class="fam-delete-btn" @click="preDeleteCheck()">Slet</button>
                <button class="cancel-btn" type="button" @click="cancel()">Annullér</button>
            </fieldset>
        </form>
    </article>

</template>

<script>

    import axios from '../http/Http.js'
    import router from '../../router.js'
    import CprLookup from '../forms/CprLookUp.vue'
    import Error from '../forms/Error.vue'
    import notify from '../notifications/Notify.js'

    export default {

        components: {
            CprLookup,
            Error
        },
        data: function() {
            return {
                create_mode: false,
                fam: {},
                showModal: false
            }
        },
        computed: {
            casid: function() {
                return this.$route.params.casid
            }
        },
        methods: {
            fetchRelation: function(famid) {
                axios.get(`/related_persons/${ famid }`)
                .then(res => {
                    this.fam = res.data
                })
                .catch(err => {
                    console.error(err)
                })
            },
            saveChanges: function() {
                if (!this.create_mode) {
                    axios.patch(`/related_persons/${ this.fam.id }/`, {
                        relation_type: this.fam.relation_type,
                        cpr_number: this.fam.cpr_number,
                        name: this.fam.name,
                        related_case: this.fam.related_case
                    })
                    .then(res => {
                        this.$router.push(`/case/${ this.casid }/`)
                    })
                    .catch(err => this.$store.dispatch('parseErrorOutput', err))
                } else {
                    axios.post(`/related_persons/`, {
                        relation_type: this.fam.relation_type,
                        cpr_number: this.fam.cpr_number,
                        name: this.fam.name,
                        related_case: this.fam.related_case,
                        main_case: this.casid,
                        from_serviceplatformen: false
                    })
                    .then(res => {
                        this.$router.push(`/case/${ this.casid }/`)
                    })
                    .catch(err => this.$store.dispatch('parseErrorOutput', err))
                }
            },
            cancel: function() {
                if (this.showModal === true) {
                    this.showModal = false
                } else {
                    this.$emit('close')
                    this.$router.push(`/case/${ this.casid }/`)
                }
            },
            preDeleteCheck: function() {
                this.showModal = true
            },
            deleteRelation: function() {
                axios.delete(`/related_persons/${ this.$route.params.famid }/`)
                .then(res => {
                    this.$emit('close')
                    this.$router.push(`/case/${ this.casid }/`)
                    notify('Relation slettet', 'success')
                })
                .catch(err => this.$store.dispatch('parseErrorOutput', err))
            }
        },
        created: function() {
            if (this.$route.params.famid) {
                this.fetchRelation(this.$route.params.famid)
            } else {
                this.create_mode = true
            }
        }
    }
    
</script>

<style>

    .familyoverview-edit {
        margin: 1rem auto;
        min-width: 20rem;
        width: auto;
    }

    .familyoverview-edit .familyoverview-edit-header {
        background-color: var(--grey2);
        padding: .5rem 2rem;
    }

    .familyoverview-edit form {
        margin: 0;
        padding: 1rem 2rem;
    }

    .familyoverview-edit input[type="text"] {
        width: 100%;
    }

    .familyoverview-edit .form-actions {
        margin: 2rem 0 1rem;
    }

    .familyoverview-edit .cancel-btn {
        float: right;
        background-color: transparent;
        color: var(--primary);
        border-color: transparent;
    }

    .familyoverview-edit .fam-delete-btn,
    .modal-delete-btn {
        margin-left: .5rem;
        border-color: var(--danger);
        color: var(--danger);
        background-color: transparent;
    }
    .modal-delete-btn {
        float: right;
        margin-left: .5rem;
    }

    .familyoverview-edit .fam-delete-btn:focus,
    .familyoverview-edit .fam-delete-btn:hover,
    .familyoverview-edit .fam-delete-btn:active,
    .modal-delete-btn:focus,
    .modal-delete-btn:hover,
    .modal-delete-btn:active {
        background-color: var(--danger);
        color: var(--grey0);
        border-color: var(--danger);
    }

</style>
