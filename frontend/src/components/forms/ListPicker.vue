<template>

    <select :id="domId" class="listpicker" @change="emitChange" v-model="selection">
        <option v-for="l in list" :value="l.id" :key="l.id">
            {{ l.name }}
        </option>
    </select>
    
</template>

<script>

    import axios from '../http/Http.js'
    
    export default {

        props: [
            'domId',
            'selectedId',
            'list'
        ],
        data: function(){
            return {
                selection: null
            }
        },
        methods: {
            setSelected: function() {
                this.selection = this.selectedId
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
