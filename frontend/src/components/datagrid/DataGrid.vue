<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <table class="datagrid">
        
        <thead>
            <tr>
                <th>
                    <input type="checkbox" id="datagrid-select-all">
                    <label for="datagrid-select-all" title="Vælg alle"></label>
                </th>
                <th v-for="key in columns"
                    :key="key"
                    @click="sortBy(key)"
                    :class="{ active: sortKey == key }">
                    {{ key | capitalize }}
                    <span class="arrow" :class="sortOrders[key] > 0 ? 'asc' : 'dsc'"></span>
                </th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="entry in filteredData" :key="entry.sbsys_id" @click="rowAction(entry)">
                <td @click.stop="">
                    <input type="checkbox" 
                           :id="`datagrid-select-${ entry.sbsys_id }`" 
                           @change="selectEntry($event, entry)">
                    <label :for="`datagrid-select-${ entry.sbsys_id }`" 
                           title="Vælg alle"></label>
                </td>
                <td v-for="key in columns" :key="key">
                    {{ entry[key] }}
                </td>
            </tr>
        </tbody>
    </table>

</template>

<script>

    export default {

        props: {
            list: Array,
            columns: Array,
            filterKey: String
        },
        data: function () {
            var sortOrders = {}
            this.columns.forEach(function (key) {
                sortOrders[key] = 1
            })
            return {
                sortKey: '',
                sortOrders: sortOrders,
                selection: []
            }
        },
        computed: {
            filteredData: function () {
                var sortKey = this.sortKey
                var filterKey = this.filterKey && this.filterKey.toLowerCase()
                var order = this.sortOrders[sortKey] || 1
                var list = this.list
                if (filterKey) {
                    list = list.filter(function (row) {
                        return Object.keys(row).some(function (key) {
                            return String(row[key]).toLowerCase().indexOf(filterKey) > -1
                        })
                    })
                }
                if (sortKey) {
                    list = list.slice().sort(function (a, b) {
                        a = a[sortKey]
                        b = b[sortKey]
                        return (a === b ? 0 : a > b ? 1 : -1) * order
                    })
                }
                return list
            }
        },
        filters: {
            capitalize: function(str) {
                return str.charAt(0).toUpperCase() + str.slice(1)
            }
        },
        methods: {
            sortBy: function(key) {
                this.sortKey = key
                this.sortOrders[key] = this.sortOrders[key] * -1
            },
            selectEntry: function(ev, entry) {
                const checked = ev.target.checked
                let idx = this.selection.findIndex(function(el) {
                    return el.sbsys_id = entry.sbsys_id
                })
                if (!checked && idx >= 0) {
                    console.log(idx)
                    this.selection.splice(idx,1)
                }
                if (checked && idx < 0) {
                    this.selection.push(entry)
                }
                this.$emit('selection', this.selection)
            },
            rowAction: function(entry) {
                this.$emit('row-action', entry)
            }
        }
    }
    
</script>

<style>

    .datagrid {
        
    }

    .datagrid th {
        background-color: var(--grey6);
        color: var(--grey2);
        cursor: pointer;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;
    }

    .datagrid th.active {
        color: #fff;
    }

    .datagrid th.active .arrow {
        opacity: 1; 
    }

    .datagrid .arrow {
        display: inline-block;
        vertical-align: middle;
        width: 0;
        height: 0;
        margin-left: 5px;
        opacity: 0.66;
    }

    .datagrid .arrow.asc {
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 4px solid #fff;
    }

    .datagrid .arrow.dsc {
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid #fff;
    }

</style>