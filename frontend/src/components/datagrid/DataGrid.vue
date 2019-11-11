<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <section class="datagrid-container">

        <header class="datagrid-header">

            <div>
                <slot name="datagrid-header"></slot>
            </div>

            <form class="datagrid-filter" @submit.prevent>
                <label for="filter-field" title="Find i liste"></label>
                <input type="search"
                    name="query" 
                    v-model="filterKey"
                    id="filter-field"
                    placeholder="Find i liste ..."
                    :disabled="dataList.length < 1 ? true : false">
            </form>

        </header>
    
        <table class="datagrid" v-if="dataList.length > 0">
            
            <thead>
                <tr>
                    <th v-if="selectable" style="width: 4.5rem;">
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
                        :class="`datagrid-filter-th ${ c.class ? c.class : '' }${ sortKey === c.key ? ' active' : '' }`">
                        <span class="arrow" :class="sortOrders[c.key] > 0 ? 'asc' : 'dsc'"></span>
                        {{ c.title }}
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="d in filteredData" :key="d.id">
                    <td v-if="selectable" style="width: 4.5rem;">
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
                        <td v-html="c.display_func ? c.display_func(d) : d[c.key]" 
                            :key="c.key" 
                            :class="c.class"
                            :title="c.display_func ? c.display_func(d) : d[c.key]">
                        </td>
                    </template>
                </tr>
                <slot name="datagrid-table-footer"></slot>
            </tbody>
        </table>

        <slot name="datagrid-footer"></slot>

    </section>

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
        user-select: none;
        vertical-align: middle;
    }

    .datagrid-filter-th {
        padding-left: 0;
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
        margin: 0 .25rem 0 .66rem;
        opacity: 0.5;
    }

    .datagrid .arrow.asc {
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid var(--grey6);
    }

    .datagrid .arrow.dsc {
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 4px solid var(--grey6);
    }

    .datagrid td {
        vertical-align: middle;
    }

    .datagrid td.datagrid-action {
        padding: 0;
    }

    .datagrid td.datagrid-action a {
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

    .datagrid-header {
        display: grid;
        grid-template-columns: auto auto;
        margin: 1rem 0;
    }

    .datagrid-filter {
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