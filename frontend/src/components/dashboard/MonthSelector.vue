<template>
    <div>
        <label for="field-month-selector">Måned</label>
        <select id="field-month-selector" :value="value" @change="changeMonth">
            <option value="1">Januar</option>
            <option value="2">Februar</option>
            <option value="3">Marts</option>
            <option value="4">April</option>
            <option value="5">Maj</option>
            <option value="6">Juni</option>
            <option value="7">Juli</option>
            <option value="8">August</option>
            <option value="9">September</option>
            <option value="10">Oktober</option>
            <option value="11">November</option>
            <option value="12">December</option>
        </select>
    </div>
</template>
<script>
export default {
    props: {
        value: {
            type: Number,
            default: Number(new Date().getUTCMonth()) + 1
        }
    },
    methods: {
        changeMonth: function(ev) {
            this.$emit('change', ev.target.value)
        }
    }
}
</script>
