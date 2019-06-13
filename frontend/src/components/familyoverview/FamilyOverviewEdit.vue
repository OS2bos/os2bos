<template>

    <article class="familyoverview-edit">
        <h1 v-if="create_mode">Opret familierelation</h1>
        <h1 v-else>Redigér familierelation</h1>
        <form @submit.prevent="saveChanges()">
            <fieldset>
                <label for="field-relation">Relation</label>
                <input id="field-relation" type="text" v-model="fam.relation_type" required>
            </fieldset>
            <fieldset>
                <label for="field-cpr">Cpr-nummer</label>
                <input id="field-cpr" type="text" v-model="fam.cpr_number" required>
            </fieldset>
            <fieldset>
                <label for="field-name">Navn</label>
                <input id="field-name" type="text" v-model="fam.name" required>
            </fieldset>
            <fieldset>
                <label for="field-sbsysid">SBSYS Hovedsag</label>
                <input id="field-sbsysid" type="text" v-model="fam.related_case" required>
            </fieldset>
            <fieldset>
                <input type="submit" value="Gem">
                <button v-if="!create_mode" class="cancel-btn" type="button" @click="cancel()">Annullér</button>
            </fieldset>
        </form>
    </article>

</template>

<script>

    import axios from '../http/Http.js'

    export default {

        props: [
            'famObj'
        ],
        data: function() {
            return {
                fam: {},
                create_mode: true
            }
        },
        methods: {
            saveChanges: function() {
                let data = {
                    relation_type: this.fam.relation_type,
                    cpr_number: this.fam.cpr_number,
                    name: this.fam.name,
                    related_case: this.fam.related_case
                }
                if (!this.create_mode) {
                    axios.get(`/related_persons/${ this.fam.id }/`, data)
                    .then(res => {
                        this.$emit('close')
                    })
                    .catch(err => console.log(err))
                } else {
                    const cas_id = this.$route.params.caseid
                    axios.post(`/related_persons/`, {
                        relation_type: this.fam.relation_type,
                        cpr_number: this.fam.cpr_number,
                        name: this.fam.name,
                        related_case: this.fam.related_case,
                        main_case: cas_id
                    })
                    .then(res => {
                        this.$router.push(`/case/${ cas_id }/`)
                    })
                    .catch(err => console.log(err))
                }
            },
            cancel: function() {
                this.$emit('close')
            }
        },
        created: function() {
            if (this.famObj) {
                this.create_mode = false
                this.fam = this.famObj
            }
        }
    }
    
</script>

<style>

    .familyoverview-edit {
        margin: 1rem;
    }

    .familyoverview-edit .cancel-btn {
        margin-left: 0.5rem;
        background-color: transparent;
        color: var(--primary);
        border-color: transparent;
    }

</style>
