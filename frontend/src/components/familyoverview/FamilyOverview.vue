<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <div class="familyoverview">

        <section v-if="!show_relations">
            <header class="familyoverview-header">
                <h2>Relationer</h2>
                <button class="fam-btn-zoom" @click="show_relations = !show_relations">
                    <span class="material-icons">zoom_in</span>
                    Vis mere
                </button>
            </header>
            <ul class="familiyoverview-minilist">
                <li v-for="relation in fam" :key="relation.id" class="familiyoverview-minilist-item">
                    <span class="fam-minilist-type">{{ relation.relation_type }}</span>
                    <span class="fam-minilist-name">{{ relation.name }}</span>
                    <span class="fam-minilist-cpr">{{ relation.cpr_number }}</span>
                </li>
            </ul>
        </section>
    
        <data-grid
            v-if="show_relations"
            ref="data-grid"
            :data-list="fam"
            :columns="columns"
            :selectable="false">

            <div class="familyoverview-header" slot="datagrid-header">
                <h2>Relationer</h2>
                <button class="fam-btn-zoom" @click="show_relations = !show_relations">
                    <span class="material-icons">zoom_out</span>
                    Vis mindre
                </button>
                <button type="submit" v-if="user_can_edit === true" class="familyoverview-create-btn" @click="$router.push(`/case/${ caseId }/familyoverview-create/`)">+ Opret relation</button>
            </div>

        </data-grid>
        <p v-if="!fam || fam.length < 1">Der er endnu ingen relationer</p>
        
    </div>

</template>

<script>

    import axios from '../http/Http.js'
    import FamilyOverviewEdit from './FamilyOverviewEdit.vue'
    import PermissionLogic from '../mixins/PermissionLogic.js'
    import DataGrid from '../datagrid/DataGrid.vue'
    import { json2jsDate } from '../filters/Date.js'
    import { userId2name } from '../filters/Labels.js'

    export default {

        mixins: [
            PermissionLogic
        ],
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
                show_relations: false,
                show_edit: false,
                columns: [
                    {
                        key: 'name',
                        title: 'Navn',
                        display_func: this.displayName,
                        class: 'fam-td-name'
                    },
                    {
                        title: 'Oprettet',
                        display_func: this.displayCreated,
                        class: 'nowrap text-center'
                    },
                    {
                        key: 'modified',
                        title: 'Dato',
                        display_func: this.displayCreatedDate,
                        class: 'nowrap text-center'
                    },
                    {
                        key: 'related_case',
                        title: 'Relateret sag',
                        display_func: this.displayRelatedCase,
                        class: 'nowrap text-center'
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
                if (this.user_can_edit === true && id.from_serviceplatformen === false) {
                    let to = `#/case/${ this.caseId }/familyoverview-edit/${ id.id }`
                    return `<span class="fam-list-type">${ id.relation_type }</span><a class="fam-list-name" href="${ to }">${ id.name }</a><span class="fam-list-cpr">${ id.cpr_number }</span>`
                } else {
                    return `<span class="fam-list-type">${ id.relation_type }</span><span class="fam-list-name">${ id.name }</span><span class="fam-list-cpr">${ id.cpr_number }</span>`
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
     
    }

    .familyoverview-header {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
        justify-content: flex-start;
    }

    .fam-btn-zoom {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
        margin: 0 0 0 1rem;
    }

    .fam-btn-zoom .material-icons {
        display: inline;
    }

    .familiyoverview-minilist {
        list-style: none;
        margin: 1rem 0 0;
        padding: 0;
    }

    .familiyoverview-minilist-item {
        display: grid;
        gap: 1rem;
        grid-template-columns: 5rem auto auto;
        border-top: solid 1px var(--grey0);
        padding: .5rem 0;
    }

    .familyoverview .datagrid-container,
    .familyoverview .datagrid {
        margin-bottom: 0;
    }

    .familyoverview .datagrid-header {
        margin-top: 0;
    }

    .familyoverview .datagrid tr {
        border: none;
    }

    .familyoverview .datagrid th,
    .familyoverview .datagrid td {
        padding: .25rem 0;
        border-bottom: solid 1px var(--grey0);
    }

    .familyoverview .datagrid th {
        background-color: transparent;
        border-bottom: solid 1px var(--grey2);
        border-top: solid 1px var(--grey2);
    }

    .familyoverview .text-center {
        text-align: center;
    }

    .fam-minilist-name {
        width: 10rem;
    }

    a.fam-list-name {
        display: inline;
    }

    a.fam-list-name:hover,
    a.fam-list-name:active,
    a.fam-list-name:focus {
        padding: 0 !important;
    }

    .fam-list-cpr {
        display: block;
    }

    .fam-list-type,
    .fam-minilist-type {
        display: block;
        opacity: .66;
        font-size: .85em;
    }

    .familyoverview-create-btn {
        margin: 0 1rem;
    }

</style>