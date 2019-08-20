<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <article class="appropriation-edit">
        <h1 v-if="create_mode">Opret bevillingskrivelse</h1>
        <h1 v-else>Redigér bevillingskrivelse</h1>
        <form @submit.prevent="saveChanges()">
            <fieldset>
                <label for="field-sbsysid">Foranstaltningssag (SBSYS-sag)</label>
                <input id="field-sbsysid" type="text" v-model="appr.sbsys_id" required @input="checkKLE(appr.sbsys_id)">
                <span class="danger" v-if="sbsysCheck">Sagsnummeret svarer ikke til en af de paragraffer, der kan vælges</span>
                <error v-if="errors && errors.sbsys_id" :msgs="errors.sbsys_id" />
            </fieldset>
            <fieldset>
                <label for="field-lawref">Bevilling efter §</label>
                <select id="field-lawref" class="listpicker" v-model="appr.section" required>
                    <option :disabled="disabled" v-for="s in sections" :value="s.id" :key="s.id">
                        {{ s.paragraph }} {{ s.text }}
                    </option>
                </select>
            </fieldset>
            <fieldset>
                <label for="field-text">Supplerende information</label>
                <textarea v-model="appr.note"></textarea>
            </fieldset>
            <fieldset>
                <input type="submit" value="Gem">
                <button class="cancel-btn" type="button" @click="cancel()">Annullér</button>
            </fieldset>
        </form>
    </article>

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
                kle: null,
                kle_regex: /\d{2}\.\d{2}\.\d{2}/,
                sections: null,
                sbsysCheck: false,
                disabled: false,
                errors: null
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
                axios.get(`/sections?allowed_for_steps=${ this.cas.effort_step }&${ this.cas_target}`)
                .then(res => {
                    this.sections = res.data
                })
                .catch(err => console.log(err))
            },
            changeSection: function(section_id) {
                this.appr.section = section_id
            },
            checkKLE: function(input) {
                this.sbsysCheck = false
                this.disabled = false
                this.kle = input.match(this.kle_regex)
                if (this.kle) {
                    let sections = this.all_sections.filter(s => s.kle_number === this.kle[0])
                    if (sections.length === 1) {
                        this.appr.section = sections[0].id
                        this.disabled = true
                    } else if (sections.length === 0) {
                        this.sbsysCheck = true
                    }
                } else {
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
                    .catch(err => { this.handleError(err) })
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
                    .catch(err => { this.handleError(err) })
                }
            },
            handleError: function(error) {
                this.errors = Error.methods.handleError(error)
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
        }
    }
    
</script>

<style>

    .appropriation-edit {
        margin: 1rem;
    }

    .appropriation-edit .cancel-btn {
        margin-left: 0.5rem;
        background-color: transparent;
        color: var(--primary);
        border-color: transparent;
    }

</style>
