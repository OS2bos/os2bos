<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <div>
        <data-grid :data-list="cases"
                   :columns="columns"
                   @selection="updateSelectedCases" />

        {{ selected_cases }}

    </div>

</template>

<script>

    import axios from '../http/Http.js'
    import DataGrid from '../datagrid/DataGrid.vue'
    import { json2js } from '../filters/Date.js'

    export default {

        components: {
            DataGrid
        },
        data: function() {
            return {
                cases: [],
                selected_cases: [],
                columns: [
                    {
                        key: 'expired',
                        title: 'Status',
                        display_func: this.displayStatus
                    },
                    {
                        key: 'sbsys_id',
                        title: 'SBSYS ID',
                        display_func: this.displayID
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
        methods: {
            update: function() {
                this.fetchCases()
            },
            fetchCases: function() {
                axios.get(`/cases/`)
                .then(res => {
                    this.cases = res.data
                })
                .catch(err => console.log(err))
            },
            updateSelectedCases: function(selections) {
                this.selected_cases = selections
            },
            displayID: function(d) {
                let to = `#/case/${ d.id }/`
                return `<a href="${ to }">${ d.sbsys_id }</a>`
            },
            displayDate: function(d) {
                return json2js(d.modified)
            },
            displayStatus: function(d) {
                if (!d.expired) {
                    return `
                        <div class="mini-label">
                            <span class="label label-GRANTED">Aktiv</span>
                        </div>
                    `
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
        
    }

</style>
