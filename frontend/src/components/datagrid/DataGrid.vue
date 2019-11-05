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
                    @click="sortBy(key)"
                    :class="{ active: sortKey == key }">
                    {{ key | capitalize }}
                    <span class="arrow" :class="sortOrders[key] > 0 ? 'asc' : 'dsc'"></span>
                </th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="entry in filteredData" @click="rowAction(entry)" :key="entry.id">
                <td @click.stop>
                    <input type="checkbox"
                           :id="`datagrid-select-${ entry.sbsys_id }`"
                           @change="selectEntry($event, entry)">
                    <label :for="`datagrid-select-${ entry.sbsys_id }`"
                           title="Vælg alle"></label>
                </td>
                <td v-for="key in columns">
                    {{ entry[key] }}
                </td>
            </tr>
        </tbody>
    </table>

</template>

<script>

    export default {

        props: {
            dataList: Array,
            columns: Array
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
                var order = this.sortOrders[sortKey] || 1
                var list = this.dataList
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
                let checked = ev.target.checked
                let idx = this.selection.findIndex(function(s) {
                    return s.id = entry.id
                })
                if (!checked && idx >= 0) {
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