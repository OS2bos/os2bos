<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <div>
        Cases

        {{ cases }}
        
        <data-grid v-if="cases" 
                   :list="cases" 
                   :columns="['status', 'sbsys_id', 'cpr_number', 'name', 'modified']" 
                   filterKey=""
                   @selection="updateSelectedCases" 
                   @row-action="navToCase" />

        {{ selected_cases }}
        
    </div>

</template>

<script>

    import axios from '../http/Http.js'
    import DataGrid from '../datagrid/DataGrid.vue'

    export default {

        components: {
            DataGrid
        },
        data: function() {
            return {
                cases: null,
                selected_cases: []
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
            navToCase: function(entry) {
                this.$router.push(`/case/${ entry.id }/`)
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
