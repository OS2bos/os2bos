<!-- This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <select :id="domId" class="listpicker" @change="emitChange" v-model="selection">
        <option v-for="l in list" :value="l.id" :key="l.id">
            {{ l[displayKey] }}
        </option>
    </select>

</template>

<script>

    import axios from '../http/Http.js'

    export default {

        props: {
            domId: String,
            selectedId: Number,
            list: Array,
            default: {
                type: Number,
                default: null
            },
            displayKey: {
                type: String,
                default: 'name'
            }
        },
        data: function(){
            return {
                selection: null
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