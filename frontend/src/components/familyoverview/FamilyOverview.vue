<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <section class="familyoverview">
            <data-grid
                ref="data-grid"
                :data-list="fam"
                :columns="columns"
                :selectable="false">

                <div class="familyoverview-header" slot="datagrid-header">
                    <h2>Familieoversigt</h2>
                   <button v-if="permissionCheck === true" class="familyoverview-create-btn" @click="$router.push(`/case/${ caseId }/familyoverview-create/`)">+ Opret relation</button>
                </div>

            </data-grid>
            <p v-if="!fam || fam.length < 1">Der er endnu ingen relationer</p>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import FamilyOverviewEdit from './FamilyOverviewEdit.vue'
    import UserRights from '../mixins/UserRights.js'
    import DataGrid from '../datagrid/DataGrid.vue'
    import { json2jsDate } from '../filters/Date.js'
    import { userId2name } from '../filters/Labels.js'

    export default {

        mixins: [UserRights],

         components: {
             FamilyOverviewEdit,
             DataGrid
        },
        props: [
            'caseId'
        ],
        data: function() {
            return {
                fam: [],
                show_edit: false,
                columns: [
                     {
                        key: 'name',
                        title: 'Navn',
                        display_func: this.displayName,
                    },
                    {
                        title: 'Oprettet',
                        display_func: this.displayCreated,
                        class: 'nowrap'
                    },
                    {
                        key: 'related_case',
                        title: 'Relateret sag',
                        display_func: this.displayRelatedCase,
                        class: 'nowrap'
                    },
                    {
                        key: 'modified',
                        title: 'Dato',
                        display_func: this.displayCreatedDate,
                        class: 'nowrap'
                    }
                ]
            }
        },
        computed: {
            cas: function() {
                return this.$store.getters.getCase
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
            },
            displayName: function(id) {
                if (this.permissionCheck === true && id.from_serviceplatformen === false) {
                    let to = `#/case/${ this.caseId }/familyoverview-edit/${ id.id }`
                    return `<a href="${ to }">${ id.name }</a><br>${ id.cpr_number }`
                } else {
                    return `${ id.name }<br>${ id.cpr_number }`
                }
            },
            displayCreatedDate: function(id) {
                return json2jsDate(id.modified)
            },
            displayRelatedCase: function(id) {
                if (id.related_case) {
                    return `${ id.related_case }`
                } else {
                    return `-`
                }
            },
            displayCreated: function(id) {
                if (id.from_serviceplatformen === true) {
                    return `Automatisk`
                } else {
                    return `${ id.user_modified }`
                }
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