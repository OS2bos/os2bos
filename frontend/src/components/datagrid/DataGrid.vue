<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <div class="datagrid-container">

        <form class="datagrid-filter" @submit.prevent>
            <label for="filter-field" title="Find i liste"></label>
            <input type="search"
                   name="query" 
                   v-model="filterKey"
                   id="filter-field"
                   placeholder="Find i liste ...">
        </form>
    
        <table class="datagrid">
            
            <thead>
                <tr>
                    <th v-if="selectable">
                        <input type="checkbox" 
                            id="datagrid-select-all"
                            @change="toggleAll($event.target.checked)">
                        <label for="datagrid-select-all" 
                            title="Vælg alle"
                            style="margin: 0;">
                        </label>
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
                    <td v-if="selectable">
                        <input type="checkbox"
                            :id="`datagrid-select-${ d.id }`"
                            @change="selectEntry($event.target.checked, d)"
                            class="datagrid-single-checkbox">
                        <label :for="`datagrid-select-${ d.id }`"
                               title="Vælg"
                               style="margin: 0;">
                        </label>
                    </td>
                    <template v-for="c in columns">
                        <td v-if="c.display_func" v-html="c.display_func(d)" :key="c.key" :class="c.clickable ? 'datagrid-td-action' : ''"></td>
                        <td v-if="!c.display_func" :key="c.key">
                            {{ d[c.key] }}
                        </td>
                    </template>
                </tr>
            </tbody>
        </table>

    </div>

</template>

<script>

    export default {

        props: {
            dataList: Array,
            columns: Array,
            selectable: Boolean
        },
        data: function () {
            var sortOrders = {}
            this.columns.forEach(function (c) {
            sortOrders[c.key] = 1
            })
            return {
                sortKey: '',
                sortOrders: sortOrders,
                selection: [],
                filterKey: ''
            }
        },
        computed: {
            filteredData: function () {
                var sortKey = this.sortKey
                var filterKey = this.filterKey && this.filterKey.toLowerCase()
                var order = this.sortOrders[sortKey] || 1
                var list = this.dataList
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

    .datagrid-container {
        margin: 0 0 1rem;
    }

    .datagrid {
        margin-top: 0;
    }

    .datagrid th {
        background-color: var(--grey0);
        color: var(--grey10);
        cursor: pointer;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;
        vertical-align: middle;
    }

    .datagrid th.active {
        color: var(--grey6);
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
        border-bottom: 4px solid var(--grey10);
    }

    .datagrid .arrow.dsc {
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid var(--grey10);
    }

    .datagrid td {
        vertical-align: middle;
    }

    .datagrid .datagrid-td-action {
        padding: 0;
    }

    .datagrid .datagrid-td-action a {
        display: block;
        border: none;
        padding: .75rem;
        border-radius: .125rem;
        transition: padding .33s;
    }

    .datagrid td a:hover,
    .datagrid td a:active {
        padding-left: 1.25rem;
    }

    .datagrid-filter {
        border-top: solid 1px var(--grey1);
        background-color: transparent;
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
        justify-content: flex-end;
        padding: .5rem 0;
        margin: 0;
    }

    .datagrid-filter label {
        margin: 0 .5rem 0 0;
    }

    .datagrid-filter input {
        width: 8.5rem;
        padding: .125rem .5rem;
        border-color: var(--grey1);
    }

</style>