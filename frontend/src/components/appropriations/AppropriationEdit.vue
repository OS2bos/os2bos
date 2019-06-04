<template>

    <article class="appropriation-edit">
        <form @submit.prevent="saveChanges()">
        <h1>Redigér bevillingskrivelse</h1>
            <fieldset>
                <label for="field-sbsysid">Foranstaltningssag (SBSYS-sag)</label>
                <input id="field-sbsysid" type="text" v-model="appr.sbsys_id">
            </fieldset>
            <fieldset>
                <label for="field-lawref">Bevilling efter §</label>
                <select id="field-lawref" class="listpicker" v-model="appr.section">
                    <option v-for="s in sections" :value="s.id" :key="s.id">
                        {{ s.paragraph }} {{ s.kle_number }} {{ s.text }}
                    </option>
                </select>
            </fieldset>
            <fieldset>
                <input type="submit" value="Gem">
                <button class="cancel-btn" type="cancel">Annullér</button>
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
                create_mode: true
            }
        },
        computed: {
            sections: function() {
                return this.$store.getters.getSections
            }
        },
        methods: {
            changeSection: function(section_id) {
                this.appr.section = section_id
            },
            saveChanges: function() {
                if (!this.create_mode) {
                    axios.patch(`/appropriations/${ this.appr.id }/`, {
                        sbsys_id: this.appr.sbsys_id,
                        section: this.appr.section
                    })
                    .then(res => {
                        this.$emit('save', res.data)
                    })
                    .catch(err => console.log(err))
                } else {
                    axios.post(`/appropriations/`, {
                        sbsys_id: this.appr.sbsys_id,
                        section: this.appr.section,
                    })
                    .then(res => {
                        this.$router.push('/')
                    })
                    .catch(err => console.log(err))
                }
            }
        },
        created: function() {
            if (this.apprObj) {
                this.create_mode = false
                this.appr = this.apprObj
            }
        }
    }
    
</script>

<style>

    .appropriation-edit {
        margin: 0;
    }

    .appropriation-edit .cancel-btn {
        margin-left: 0.5rem;
        background-color: transparent;
        color: var(--primary);
        border-color: transparent;
    }

</style>
