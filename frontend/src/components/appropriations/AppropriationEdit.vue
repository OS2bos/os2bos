<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <section class="appropriation-edit">
        <header class="appropriation-edit-header">
            <h1 v-if="create_mode">Opret bevillingskrivelse</h1>
            <h2 v-else>Redigér bevillingskrivelse</h2>
        </header>
        <form @submit.prevent="saveChanges()">
            <error />
            <fieldset>
                <label class="required" for="field-sbsysid">Foranstaltningssag (SBSYS-sag)</label>
                <input id="field-sbsysid" type="text" v-model="appr.sbsys_id" @input="checkKLE(appr.sbsys_id)" required>
                <p class="danger" v-if="sbsysCheck">Sagsnummeret svarer ikke til en af de paragraffer, der kan vælges.</p>
                <error err-key="sbsys_id" />
            
                <label class="required" for="field-lawref">Bevilling efter §</label>
                <select id="field-lawref" class="listpicker" v-model="appr.section" required>
                    <option v-for="s in sections" :value="s.id" :key="s.id">
                        {{ s.paragraph }} {{ s.text }}
                    </option>
                </select>

                <label for="field-text">Supplerende information</label>
                <textarea id="field-text" v-model="appr.note"></textarea>
            </fieldset>
            <fieldset class="form-actions">
                <input type="submit" value="Gem">
                <button class="cancel-btn" type="button" @click="cancel()">Annullér</button>
            </fieldset>
        </form>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import Error from '../forms/Error.vue'

    export default {

        components: {
            Error
        },
        props: [
            'apprObj'
        ],
        data: function() {
            return {
                appr: {},
                create_mode: true,
                kle_regex: /\d{2}\.\d{2}\.\d{2}/,
                sections: null,
                sbsysCheck: false
            }
        },
        computed: {
            cas: function() {
                return this.$store.getters.getCase
            },
            cas_target: function() {
                if (this.cas.target_group === 'FAMILY_DEPT') {
                    return 'allowed_for_family_target_group=true'
                } else if (this.cas.target_group === 'DISABILITY_DEPT') {
                    return 'allowed_for_disability_target_group=true'
                } else {
                    return ''
                }
            },
            all_sections: function() {
                return this.$store.getters.getSections
            }
        },
        methods: {
            fetchSections: function() {
                axios.get(`/sections/?allowed_for_steps=${ this.cas.effort_step }&${ this.cas_target}`)
                .then(res => {
                    this.sections = res.data
                })
                .catch(err => console.log(err))
            },
            changeSection: function(section_id) {
                this.appr.section = section_id
            },
            checkKLE: function(input) {
                let kle = input.match(this.kle_regex)
                this.sbsysCheck = false
                if (kle) {
                    axios.get(`/sectioninfos/?kle_number=${ kle[0] }`)
                    .then(res => {
                        if (res.data.length === 1) {
                            this.appr.section = res.data[0].section
                            this.$forceUpdate()
                        } else if (res.data.length === 0) {
                            this.appr.section = null
                            this.sbsysCheck = true
                        }
                    })
                    .catch(err => {
                        console.log(err)
                    })
                } else {
                    this.sbsysCheck = true
                    return false
                }                
            },
            saveChanges: function() {
                if (!this.create_mode) {
                    axios.patch(`/appropriations/${ this.appr.id }/`, {
                        sbsys_id: this.appr.sbsys_id,
                        section: this.appr.section,
                        note: this.appr.note
                    })
                    .then(res => {
                        this.$emit('close')
                    })
                    .catch(err => this.$store.dispatch('parseErrorOutput', err))
                } else {
                    const cas_id = this.$route.params.caseid
                    axios.post(`/appropriations/`, {
                        sbsys_id: this.appr.sbsys_id,
                        section: this.appr.section,
                        note: this.appr.note,
                        status: 'DRAFT',
                        case: cas_id
                    })
                    .then(res => {
                        this.$router.push(`/appropriation/${ res.data.id }/`)
                    })
                    .catch(err => this.$store.dispatch('parseErrorOutput', err))
                }
            },
            cancel: function() {
                if (!this.create_mode) {
                    this.$emit('close')
                    this.$router.push(`/appropriation/${ this.appr.id }/`) 
                } else {
                    this.$emit('close')
                    this.$router.push(`/case/${ this.$route.params.caseid }/`) 
                }
            }
        },
        created: function() {
            this.fetchSections()
            if (this.apprObj) {
                this.create_mode = false
                this.appr = this.apprObj
            }
            this.$store.commit('clearErrors')
        }
    }
    
</script>

<style>

    .appropriation-edit {
        margin: 1rem auto;
    }

    .appropriation-edit .appropriation-edit-header {
        background-color: var(--grey2);
        padding: .5rem 2rem;
    }

    .appropriation-edit form {
        padding: 1rem 2rem 0;
    }

    .appropriation-edit .form-actions {
        padding: 0 0 2rem;
    }

    .appropriation-edit .cancel-btn {
        margin-left: 0.5rem;
        background-color: transparent;
        color: var(--primary);
        border-color: transparent;
    }

</style>
