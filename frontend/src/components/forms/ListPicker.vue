<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <div>
    <select 
        :id="domId" 
        class="listpicker" 
        v-model="selected" 
        :required="required">
        <option value="">---</option>
        <option 
            v-for="l in sorted_list"
            :value="l.id.toString()"
            :key="l.id">
            <span v-if="l.active === false">(</span>
            {{ l[displayKey] }} {{ l[displayKey2] }}
            <span v-if="l.active === false">)</span>
        </option>
    </select>
    </div>
</template>

<script>
    import Vue from 'vue'

    export default {

        props: {
            domId: String,
            selectedId: [Number, String],
            list: [Array, Boolean],
            defaultValue: {
                type: [Number, String],
                default: ''
            },
            displayKey: {
                type: String,
                default: 'name'
            },
            displayKey2: {
                type: String
            },
            required: Boolean
        },
        data: function(){
            return {
                selected: this.selectedId ? this.selectedId.toString() : this.defaultValue.toString(),
                sorted_list: this.sortOptionList(this.list)
            }
        },
        watch: {
            selectedId: function(new_val) {
                if (new_val) {
                    this.selected = new_val.toString()
                }
            },
            selected: function(new_val, old_val) {
                if (new_val !== old_val) {
                    this.$emit('selection', new_val.toString())
                }
            },
            list: function(new_val, old_val) {
                if (new_val !== old_val) {
                    this.sorted_list = this.sortOptionList(this.list)
                }
            }
        },
        methods: {
            sortOptionList: function(arr) {
                if (arr) {
                    let list = arr
                    list = list.slice().sort(function (a, b) {
                        let nameA = a.name || a.fullname
                        let nameB = b.name || b.fullname
                        if (nameA < nameB) {
                            return -1
                        }
                        if (nameA > nameB) {
                            return 1
                        }
                        return 0
                    })
                    return list
                } else {
                    return []
                }
            }
        }
    }
</script>

<style>

    .listpicker {
        width: 100%;
    }

</style>