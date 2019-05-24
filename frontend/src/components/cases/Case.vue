<template>

    <section class="case" v-if="cas">

        <header class="case-header">
            <h1 style="padding: 0;">
                <i class="material-icons">folder_shared</i>
                Hovedsag {{ cas.sbsys_id }}
            </h1>
            <button @click="edit_mode = !edit_mode">Redigér</button>
        </header>

        <div class="case-info" v-if="!edit_mode">
            <dl style="flex: 1 0 33%;">
                <dt>Sagspart (CPR, navn)</dt>
                <dd>{{ cas.cpr_number }}, {{ cas.name }}</dd>
                <dt>Indsatstrappen:</dt>
                <dd>ikke implementeret</dd>
                <dt>Skaleringstrappe:</dt>
                <dd>ikke implementeret</dd>
            </dl>
            <dl style="flex: 1 0 33%;">
                <dt>Sagsbehander:</dt>
                <dd>{{ cas.case_worker }}</dd>
                <dt>Team:</dt>
                <dd>ikke implementeret</dd>
                <dt>Distrikt:</dt>
                <dd>{{ cas.district}}</dd>
                <dt>Leder:</dt>
                <dd>ikke implementeret</dd>
            </dl>
            <dl style="flex: 1 0 33%;">
                <dt>Betalingskommune:</dt>
                <dd>{{ cas.paying_municipality }}</dd>
                <dt>Handlekommune:</dt>
                <dd>{{ cas.acting_municipality }}</dd>
                <dt>Bopælsskommune:</dt>
                <dd>{{ cas.residence_municipality }}</dd>
            </dl>
        </div>

        <form v-if="edit_mode" @submit.prevent="saveChanges()">
            <fieldset>
                <label for="field-name">Sagspart, navn</label>
                <input id="field-name" type="text" v-model="cas.name">
            </fieldset>
            <fieldset>
                <label for="field-cpr">Sagspart, CPR-nr</label>
                <input id="field-cpr" type="text" v-model="cas.cpr_number">
            </fieldset>
            <fieldset>
                <input type="submit" value="Gem">
                <button type="cancel">Annullér</button>
            </fieldset>
        </form>

        <appropriations :case-id="cas.id" />

    </section>

</template>

<script>

    import Appropriations from '../appropriations/AppropriationList.vue'
    import axios from '../http/Http.js'

    export default {

        components: {
            Appropriations
        },
        
        data: function() {
            return {
                cas: null,
                edit_mode: false
            }
        },
        methods: {
            update: function() {
                this.fetchCase(this.$route.params.id)
            },
            fetchCase: function(id) {
                axios.get(`/cases/${id}/`)
                .then(res => {
                    this.cas = res.data
                    this.$store.commit('setBreadcrumb', [
                        {
                            link: '/',
                            title: 'Mine sager'
                        },
                        {
                            link: false,
                            title: `${ this.cas.sbsys_id}, ${ this.cas.name}`
                        }
                    ])
                })
                .catch(err => console.log(err))
            },
            saveChanges: function() {
                axios.patch(`/cases/${ this.cas.id }/`, {
                    name: this.cas.name,
                    cpr_number: this.cas.cpr_number
                })
                .then(() => {
                    this.edit_mode =  false
                    this.update()
                })
                .catch(err => console.log(err))
            }
        },
        created: function() {
            this.update()
        }
        
    }
    
</script>

<style>

    .case {
        margin: 1rem;
    }

    .case-header {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
    }

    .case-header > button {
        margin: 1rem;
    }

    .case-info {
        display: flex; 
        flex-flow: row nowrap;
        background-color: var(--grey1);
        padding: 1rem 2rem;
    }

</style>
