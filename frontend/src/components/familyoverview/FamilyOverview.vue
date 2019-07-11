<template>
    <section class="familyoverview">
        <header class="familyoverview-header">
            <h1>Familieoversigt</h1>
            <button class="familyoverview-create-btn" @click="$router.push(`/case/${ caseId }/familyoverview-create/`)">+ Opret familierelation</button>
        </header>
        <table class="familyoverview-list" v-if="fam && fam.length > 0">
            <thead>
                <tr>
                    <th>Relation</th>
                    <th>Borger</th>
                    <th>Sag</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="f in fam" :key="f.id">
                    <td>{{ f.relation_type }}</td>
                    <td>{{ f.cpr_number }} - {{ f.name }}</td>
                    <td>
                        <span v-if="!f.related_case">-</span>
                        {{ f.related_case }}
                    </td>
                    <td>
                        <router-link :to="`/case/${ caseId }/familyoverview-edit/${ f.id }`" class="edit-icon">
                            <i class="material-icons">edit</i>
                        </router-link>
                    </td>
                </tr>
            </tbody>
        </table>
        <p v-if="!fam || fam.length < 1">Der er endnu ingen relationer</p>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import FamilyOverviewEdit from './FamilyOverviewEdit.vue'

    export default {

         components: {
             FamilyOverviewEdit
        },
        props: [
            'caseId'
        ],
        data: function() {
            return {
                fam: null,
                show_edit: false
            }
        },
        methods: {
            fetchFamilyOverview: function() {
                axios.get(`/related_persons/?main_case=${ this.caseId }`)
                .then(res => {
                    this.fam = res.data
                })
                .catch(err => console.log(err))
            }
        },
        created: function() {
            this.fetchFamilyOverview()
        }
    }
    
</script>

<style>

    .familyoverview {
        margin: 2rem 0;
    }

    .familyoverview-header {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
        justify-content: flex-start;
    }

    .familyoverview-create-btn {
        margin: 0 1rem;
    }

    .familyoverview a.edit-icon {
        border: none;
    }

</style>