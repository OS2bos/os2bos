<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <select :id="domId" class="listpicker" @change="emitChange" v-model="selection" :required="required">
        <option :value="null">---</option>
        <option 
            v-for="l in sortList" 
            :value="l.id" 
            :key="l.id">
            <span v-if="l.active === false">(</span>
            {{ l[displayKey] }} {{ l[displayKey2]}}
            <span v-if="l.active === false">)</span>
        </option>
    </select>

</template>

<script>

    export default {

        props: {
            domId: String,
            selectedId: [Number, String],
            list: [Array, Boolean],
            default: {
                type: [Number, String],
                default: null
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
                selection: null
            }
        },
        computed: {
            sortList: function () {
                let list = this.list
                if (list) {
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
                }
                return list
            }
        },
        watch: {
            selectedId: function() {
                this.setSelected()
            }
        },
        methods: {
            setSelected: function() {
                if (this.selectedId) {
                    this.selection = this.selectedId
                } else {
                    this.selection = this.default
                    this.$emit('selection', this.default)
                }
            },
            emitChange: function() {
                this.$emit('selection', this.selection)
            }
        },
        created: function() {
            this.setSelected()
        }

    }

</script>

<style>

    .listpicker {
        width: 100%;
    }

</style>