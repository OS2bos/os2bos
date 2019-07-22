<template>

    <article class="appropriation-edit">
        <h1 v-if="create_mode">Opret bevillingskrivelse</h1>
        <h1 v-else>Redigér bevillingskrivelse</h1>
        <form @submit.prevent="saveChanges()">
            <fieldset>
                <label for="field-sbsysid">Foranstaltningssag (SBSYS-sag)</label>
                <input id="field-sbsysid" type="text" v-model="appr.sbsys_id" required @input="checkKLE(appr.sbsys_id)">
            </fieldset>
            <fieldset>
                <label for="field-lawref">Bevilling efter §</label>
                <select id="field-lawref" class="listpicker" v-model="appr.section" required>
                    <option v-for="s in sections" :value="s.id" :key="s.id">
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

    export default {

        props: [
            'apprObj'
        ],
        data: function() {
            return {
                appr: {},
                create_mode: true,
                kle: null,
                kle_regex: /\d{2}\.\d{2}\.\d{2}/,
                sections: null
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
                this.kle = input.match(this.kle_regex)
                if (this.kle) {
                    let sections = this.all_sections.filter(s => s.kle_number === this.kle[0])
                    if (sections.length === 1) {
                        this.appr.section = section.id
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
                    .catch(err => console.log(err))
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
                    .catch(err => console.log(err))
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
