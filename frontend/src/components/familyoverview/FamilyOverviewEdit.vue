<template>

    <article class="familyoverview-edit">
        <h1 v-if="create_mode">Opret familierelation</h1>
        <h1 v-else>Redigér familierelation</h1>
        <form @submit.prevent="saveChanges()">
            <fieldset>
                <label for="field-cpr">Cpr-nummer</label>
                <input id="field-cpr" type="text" v-model="fam.cpr_number" required @input="lookupCPR(fam.cpr_number)">
            </fieldset>
            <fieldset>
                <label for="field-name">Navn</label>
                <input id="field-name" type="text" v-model="fam.name" required>
            </fieldset>
            <fieldset>
                <label for="field-relation">Relation</label>
                <input id="field-relation" type="text" v-model="fam.relation_type" required>
            </fieldset>
            <fieldset>
                <label for="field-sbsysid">SBSYS Hovedsag</label>
                <input id="field-sbsysid" type="text" v-model="fam.related_case">
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
import router from '../../router.js';

    export default {

        data: function() {
            return {
                create_mode: false,
                fam: {}
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
                    console.log(err)
                })
            },
            lookupCPR: function(cpr_no) {
                const cpr = cpr_no.replace('-','')
                if (cpr.length > 9) {
                    axios.get(`/related_persons/fetch_from_serviceplatformen/?cpr=${ cpr }`)
                    .then(res => {
                        this.fam.name = res.data[0].name
                        this.fam.relation_type = res.data[0].relation_type
                        this.$forceUpdate()
                    })
                    .catch(err => console.log(err))
                }  
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
                    .catch(err => console.log(err))
                } else {
                    axios.post(`/related_persons/`, {
                        relation_type: this.fam.relation_type,
                        cpr_number: this.fam.cpr_number,
                        name: this.fam.name,
                        related_case: this.fam.related_case,
                        main_case: this.casid
                    })
                    .then(res => {
                        this.$router.push(`/case/${ this.casid }/`)
                    })
                    .catch(err => console.log(err))
                }
            },
            cancel: function() {
                this.$emit('close')
                this.$router.push(`/case/${ this.casid }/`)
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
        margin: 1rem;
    }

    .familyoverview-edit .cancel-btn {
        margin-left: 0.5rem;
        background-color: transparent;
        color: var(--primary);
        border-color: transparent;
    }

</style>
