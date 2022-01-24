<!-- Copyright (C) 2022 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <data-grid
        class="export-data-grid"
        :data-list="appropriations"
        :columns="columns"
        :selectable="false">
    </data-grid>

</template>

<script>
    import DataGrid from '../datagrid/DataGrid.vue'
    import {json2jsDate} from '../filters/Date.js'

    export default {
        components: {
            DataGrid
        },
        props: [
            'appropriations'
        ],
        data: function () {
            return {
                columns: [
                    {
                        key: 'case_cpr',
                        title: 'CPR'
                    },
                    {
                        key: 'sbsysId',
                        title: 'Bevilling',
                        display_func: function(d) {
                            let to = `#/appropriation/${ d.pk }/`
                            return `
                                <a href="${ to }">
                                    <i class="material-icons">folder_open</i>
                                    ${ d.sbsysId }
                                </a>
                            `
                        },
                        class: 'datagrid-action nowrap'
                    },
                    {
                        key: 'main_activity_name',
                        title: 'Hovedydelse',
                        display_func: function(d) {
                            let to = `#/activity/${ d.main_activity_pk }/`
                            return `<a href="${ to }"><i class="material-icons">style</i> ${ d.main_activity_name }</a>`
                        },
                        class: 'datagrid-action nowrap'
                    },
                    {
                        key: 'main_activity_startdate',
                        display_func: function(d) {
                            return json2jsDate(d.main_activity_startdate)
                        },
                        title: 'Startdato'
                    },
                    {
                        key: 'main_activity_enddate',
                        display_func: function(d) {
                            return json2jsDate(d.main_activity_enddate)
                        },
                        title: 'Slutdato'
                    },
                    {
                        key: 'dst_report_type',
                        title: 'Ny/Ændret',
                        display_func: function(d) {
                            return `<span class="datagrid-${ d.dst_report_type }">${ d.dst_report_type ? d.dst_report_type : 'Uændret' }</span>`
                        }
                    }
                ]
            }
        }
    }
    
</script>

<style>
    .export-data-grid .datagrid-header {
        display: none;
    }
    .export-data-grid .datagrid-Ny::before,
    .export-data-grid .datagrid-Ændring::before {
        content: '';
        margin-right: .5rem;
        border-radius: 50%;
        width: 1rem;
        height: 1rem;
        overflow: hidden;
        display: inline-block;
        vertical-align: middle;
    }
    .export-data-grid .datagrid-Ny::before { 
        background-color: var(--success);
    }
    .export-data-grid .datagrid-Ændring::before {
        background-color: var(--warning);
    }
</style>