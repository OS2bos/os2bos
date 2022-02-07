<template>
    <div>
        <label for="field-year-selector" class="sr-only">År</label>
        <select id="field-year-selector" :value="value" @change="changeYear">
            <option :value="current_year">{{ current_year }}</option>
            <option v-for="year in years" :value="year" :key="year">{{ year }}</option>
        </select>
    </div>
</template>
<script>
export default {
    props: {
        value: {
            type: Number,
            default: new Date().getUTCFullYear()
        }
    },
    data: function() {
        return {
            current_year: new Date().getUTCFullYear(),
            years: []
        }
    },
    methods: {
        changeYear: function(ev) {
            this.$emit('change', ev.target.value)
        },
        generateYears: function(base_year) {
            let years = []
            for (let i = -10; i <= 10; i++) {
                years.push(base_year + i)
            }
            return years
        }
    },
    created: function() {
        this.years = this.generateYears(this.current_year)
    }
}
</script>
