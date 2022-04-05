<template>
    <div>
        <label class="required" for="field-lawref">Bevillingsparagraf</label>
        <select id="field-lawref" :value="value" @change="changeParagraph">
            <option 
                v-for="s in all_sections"
                :value="s.id"
                :key="s.id">
                <span v-if="s.active === false">(</span>
                {{ s.paragraph }} {{ s.text }}
                <span v-if="s.active === false">)</span>
            </option>
        </select>
    </div>
</template>
<script>
export default {
    props: [
        'value'
    ],
    computed: {
        all_sections: function() {
            return this.$store.getters.getSections
        }
    },
    methods: {
        changeParagraph: function(ev) {
            this.$emit('change', ev.target.value)
        }
    }
}
</script>
