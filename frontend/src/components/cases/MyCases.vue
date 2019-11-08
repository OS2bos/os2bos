<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <section class="cases" v-if="cas">
    
        <data-grid ref="data-grid"
                    :data-list="cas"
                    :columns="columns"
                    :selectable="false">

            <div slot="datagrid-header" class="cases-header">
                <h1 style="padding: 0;">Mine sager</h1>
                <button v-if="permissionCheck === true" class="create" @click="$router.push('/case-create/')">+ Tilknyt hovedsag</button>
            </div>

            <p slot="datagrid-footer" v-if="cas.length < 1">
                Der er ikke tilknyttet nogen sager
            </p>

        </data-grid>
    
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import { json2js } from '../filters/Date.js'
    import UserRights from '../mixins/UserRights.js'
    import DataGrid from '../datagrid/DataGrid.vue'

    export default {

        mixins: [UserRights],
        components: {
            DataGrid
        },
        data: function() {
            return {
                cas: null,
                columns: [
                    {
                        key: 'expired',
                        title: 'Status',
                        display_func: this.displayStatus,
                        class: 'datagrid-td-status'
                    },
                    {
                        key: 'sbsys_id',
                        title: 'SBSYS ID',
                        display_func: this.displayID,
                        class: 'datagrid-action'
                    },
                    {
                        key: 'cpr_number',
                        title: 'CPR nr.',
                    },
                    {
                        key: 'name',
                        title: 'Navn',
                    },
                    {
                        key: 'modified',
                        title: 'Ændret',
                        display_func: this.displayDate
                    }
                ]
            }
        },
        computed: {
            user: function() {
                return this.$store.getters.getUser
            }
        },
        watch: {
            user: function() {
                this.update()
            }
        },
        methods: {
            update: function() {
                this.fetchCases()
            },
            fetchCases: function() {
                if (this.user) {
                    axios.get(`/cases/?case_worker=${ this.user.id }&expired=false`)
                    .then(res => {
                        this.cas = res.data
                    })
                    .catch(err => console.log(err))
                }
            },
            displayID: function(d) {
                let to = `#/case/${ d.id }/`
                return `<a href="${ to }"><i class="material-icons">folder_shared</i> ${ d.sbsys_id }</a>`
            },
            displayDate: function(d) {
                return json2js(d.modified)
            },
            displayStatus: function(d) {
                if (!d.expired) {
                    return `<div class="mini-label"><span class="label label-GRANTED">Aktiv</span></div>`
                }   
            }
        },
        created: function() {
            this.update()
        }
        
    }
    
</script>

<style>

    .cases {
        margin: 0 2rem 2rem;
    }

    .cases-header {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
    }

    .cases .create {
        margin: 0 0 0 1.5rem;
    }

    .datagrid-td-status {
        width: 8rem;
    }

    th.datagrid-td-status {
        padding-left: 1rem;
    }

</style>
