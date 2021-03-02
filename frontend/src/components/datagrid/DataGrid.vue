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

            <!-- Disable filter -->
            <!-- <form class="datagrid-filter" @submit.prevent>
                <label :for="`filter-field-${ componentId }`" title="Find i liste"></label>
                <input type="search"
                    name="query"
                    v-model="filterKey"
                    :id="`filter-field-${ componentId }`"
                    placeholder="Find i liste ..."
                    :disabled="dataList.length < 1 ? true : false">
            </form> -->

        </header>
    
        <table class="datagrid" v-if="filteredData.length > 0">
            
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
                        <span v-if="c.key" class="datagrid-th-arrow" :class="sortOrders[c.key] > 0 ? 'asc' : 'dsc'"></span>
                        <span class="datagrid-th-title">{{ c.title }}</span>
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="d in filteredData" :key="d.id" :class="`datagrid-r-${ d.id}`">
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
                        <td v-if="c.display_component"
                            :key="c.key" 
                            :class="c.class"
                            :title="d[c.key]">
                            <virtual-component :component="c.display_component" :rowid="d.id" :compdata="d" @update="emitUpdate"></virtual-component>
                        </td>
                        <td v-else
                            :key="c.key" 
                            :class="c.class"
                            :title="d[c.key]"
                            v-html="c.display_func ? c.display_func(d) : d[c.key]">
                        </td>
                    </template>
                </tr>
                <slot name="datagrid-table-footer"></slot>
            </tbody>
        </table>

        <slot name="datagrid-footer"></slot>

        <p v-if="filteredData.length < 1 && filterKey">Kan ikke finde nogen resultater, der matcher de valgte kriterier</p>

    </section>

</template>

<script>

    import Vue from 'vue'

    const VirtualComponent = Vue.component('virtual-component', {
        render: function (createElement) {
            return createElement(this.component, {
                props: {
                    rowid: this.rowid,
                    compdata: this.compdata
                },
                on: {
                    update: this.emitUpdate
                }
            })
        },
        props: [
            'rowid',
            'compdata',
            'component'
        ],
        methods: {
            emitUpdate: function(new_data) {
                this.$emit('update', new_data)
            }
        }
    })

    export default {

        props: {
            dataList: [Array, Boolean],
            columns: Array,
            selectable: Boolean
        },
        components: {
            VirtualComponent
        },
        data: function () {
            var sortOrders = {}
            this.columns.forEach(function (c) {
                sortOrders[c.key] = 1
            })
            return {
                componentId: null,
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
                    list = list.filter((row) => {
                        let fewer_keys = Object.keys(row)
                        fewer_keys = fewer_keys.filter((key) => {
                            for (let column in this.columns) {
                                if (this.columns[column].key === key) { // Add "&& this.columns[column].searchable !== false" if you want to exclude some columns in searches
                                    return key
                                }
                            }
                        })
                        return fewer_keys.some(function (key) {
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
                if (key) {
                    this.sortKey = key
                    this.sortOrders[key] = this.sortOrders[key] * -1
                }
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
            },
            emitUpdate: function(new_data) {
                this.$emit('update', new_data)
            }
        },
        mounted: function() {
            this.componentId = this._uid
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
        opacity: .66;
        cursor: pointer;
        user-select: none;
        vertical-align: middle;
        font-weight: normal;
        font-size: .85rem;
    }

    .datagrid-filter-th {
        padding-left: 0;
        white-space: nowrap;
    }

    .datagrid th.active {
        color: var(--grey6);
    }

    .datagrid th.active .datagrid-th-arrow {
        opacity: 1; 
    }

    .datagrid .datagrid-th-arrow {
        display: inline-block;
        vertical-align: middle;
        width: 0;
        height: 0;
        margin: 0 .25rem 0 .5rem;
        opacity: 0.5;
    }

    .datagrid .datagrid-th-arrow.asc {
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid var(--grey6);
    }

    .datagrid .datagrid-th-arrow.dsc {
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 4px solid var(--grey6);
    }

    .datagrid td {
        vertical-align: middle;
        padding: .5rem;
    }

    .datagrid td:first-child {
        padding-left: 1.5rem;
    }

    .datagrid td.datagrid-action {
        padding: 0;
    }

    .datagrid td.datagrid-action > a:link,
    .datagrid td.datagrid-action > a:visited,
    .datagrid button.datagrid-action-btn {
        display: block;
        border: none;
        padding: .75rem;
        background-color: transparent;
        text-align: left;
        transition: transform .33s;
        box-shadow: none;
        font-size: 1rem;
        height: auto;
        margin: 0;
    }

    .datagrid td.datagrid-action > a:hover,
    .datagrid td.datagrid-action > a:active,
    .datagrid td.datagrid-action > a:focus,
    .datagrid button.datagrid-action-btn:hover,
    .datagrid button.datagrid-action-btn:active,
    .datagrid button.datagrid-action-btn:focus {
        transform: translate(.5rem,0);
        color: var(--grey10);
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