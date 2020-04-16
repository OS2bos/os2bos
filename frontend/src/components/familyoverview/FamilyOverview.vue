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
            <button v-if="permissionCheck === true" class="familyoverview-create-btn" @click="$router.push(`/case/${ caseId }/familyoverview-create/`)">+ Opret relation</button>
        </header>
        <ul class="familyoverview-list list" v-if="fam && fam.length > 0">
            <li v-for="f in fam" :key="f.id" class="familyoverview-list-item">
                <dl>
                    <dt class="relation">{{ f.relation_type }}</dt>
                    <dd class="person">
                        {{ f.cpr_number }},
                        <router-link v-if="permissionCheck === true" :to="`/case/${ caseId }/familyoverview-edit/${ f.id }`">
                            {{ f.name }}
                        </router-link>
                        <span v-if="permissionCheck === false">{{ f.name }}</span>
                    </dd>
                </dl>
                <dl v-if="f.related_case" style="margin-left: 1rem;">
                    <dt>Relateret sag</dt>
                    <dd>{{ f.related_case }}</dd>
                </dl>
            </li>
        </ul>
        <p v-if="!fam || fam.length < 1">Der er endnu ingen relationer</p>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import FamilyOverviewEdit from './FamilyOverviewEdit.vue'
    import UserRights from '../mixins/UserRights.js'

    export default {

        mixins: [UserRights],

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

    .familyoverview {
        max-width: 40rem;
    }

    .familyoverview-header {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
        justify-content: flex-start;
    }

    .familyoverview-list {
        margin-top: 1rem;
    }

    .familyoverview-list .relation {
        display: inline-block;
        text-transform: capitalize;
        min-width: 6rem;
    }

    .familyoverview .familyoverview-list-item {
        display: flex;
        flex-flow: row nowrap;
        background-color: var(--grey1);
        padding: .25rem 1rem .5rem;
        margin: 0 0 .125rem;

    }

    .familyoverview-create-btn {
        margin: 0 1rem;
    }

</style>