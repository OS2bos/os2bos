<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <section class="familyoverview">
        <header class="familyoverview-header">
            <h2>Familieoversigt</h2>
            <button class="familyoverview-create-btn" @click="$router.push(`/case/${ caseId }/familyoverview-create/`)">+ Opret familierelation</button>
        </header>
        <table class="familyoverview-list" v-if="fam && fam.length > 0">
            <thead>
                <tr>
                    <th>Relation</th>
                    <th>Person</th>
                    <th>Relateret sag</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="f in fam" :key="f.id">
                    <td style="text-transform: capitalize;">{{ f.relation_type }}</td>
                    <td>
                        <p class="person-info">
                            <router-link :to="`/case/${ caseId }/familyoverview-edit/${ f.id }`">
                                {{ f.cpr_number }}
                            </router-link>  
                            <router-link :to="`/case/${ caseId }/familyoverview-edit/${ f.id }`">
                                {{ f.name }}
                            </router-link>  
                        </p>
                    </td>
                    <td>
                        {{ f.related_case }}
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
        watch: {
          caseId: function() {
            this.fetchFamilyOverview()
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

    .familyoverview-header {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
        justify-content: flex-start;
    }

    .familyoverview-list th,
    .familyoverview-list td {
        padding: .5rem 1rem;
    }

    .familyoverview-list .person-info {
        display: flex;
        flex-flow: row wrap;
    }

    .familyoverview-list .person-info a:first-child {
        margin-right: .5rem;
    }

    .familyoverview-create-btn {
        margin: 0 1rem;
    }

</style>