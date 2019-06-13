<template>
    <section class="familyoverview">
        <header class="familyoverview-header">
            <h1>Familieoversigt</h1>
            <button class="familyoverview-create-btn" @click="$router.push(`/case/${ caseId }/familyoverview-create/`)">+ Opret familierelation</button>
        </header>
        <!-- <div v-if="show_edit">
            <family-overview-edit :fam-obj="fam" v-if="show_edit" @close="update()" />
        </div> -->
        <table class="familyoverview-list">
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
                    <td>{{ f.related_case }}</td>
                    <td>
                        <!-- <button @click="show_edit = !show_edit" class="familyoverview-create-btn"><i class="material-icons">edit</i></button> -->
                        <router-link :to="`/case/${ caseId }/familyoverview-edit/${ f.id }`">
                            <i class="material-icons edit-icon">edit</i>
                        </router-link>
                    </td>
                </tr>
            </tbody>
        </table>
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

    .edit-icon {
        font-size: 1rem;
    }

</style>