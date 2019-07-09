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