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
                    <input type="checkbox" 
                           id="datagrid-select-all"
                           @change="toggleAll($event.target.checked)">
                    <label for="datagrid-select-all" 
                           title="Vælg alle"></label>
                </th>
                <th v-for="c in columns" 
                    :key="c.key"
                    @click="sortBy(c.key)"
                    :class="{ active: sortKey == c.key }">
                    {{ c.title }}
                    <span class="arrow" :class="sortOrders[c.key] > 0 ? 'asc' : 'dsc'"></span>
                </th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="d in filteredData" :key="d.id">
                <td>
                    <input type="checkbox"
                           :id="`datagrid-select-${ d.id }`"
                           @change="selectEntry($event.target.checked, d)"
                           class="datagrid-single-checkbox">
                    <label :for="`datagrid-select-${ d.id }`"
                           title="Vælg"></label>
                </td>
                <td v-for="c in columns" :key="c.key">
                    {{ d[c.key] }}
                </td>
            </tr>
        </tbody>
    </table>

</template>

<script>

    export default {

        props: {
            dataList: Array,
            columns: Array,
            filterKey: String
        },
        data: function () {
            var sortOrders = {}
            this.columns.forEach(function (c) {
            sortOrders[c.key] = 1
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
        methods: {
            sortBy: function(key) {
                this.sortKey = key
                this.sortOrders[key] = this.sortOrders[key] * -1
            },
            toggleAll(check) {
                let checkboxes = document.querySelectorAll('.datagrid-single-checkbox')
                if (check) {
                    checkboxes.forEach(function(node) {
                        node.checked = true
                    })
                    this.selection = this.dataList.slice(0, this.dataList.length + 1)
                } else {
                    checkboxes.forEach(function(node) {
                        node.checked = false
                    })
                    this.selection = []
                }
                this.$emit('selection', this.selection)
            },
            selectEntry: function(checked, entry) {
                let idx = this.selection.findIndex(function(s) {
                    return s.id === entry.id
                })
                if (!checked && idx >= 0) {
                    this.selection.splice(idx,1)
                }
                if (checked && idx < 0) {
                    this.selection.push(entry)
                }
                this.$emit('selection', this.selection)
            }
        }
    }
    
</script>

<style>

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