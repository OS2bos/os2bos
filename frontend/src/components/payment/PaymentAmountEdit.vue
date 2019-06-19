<template>

    <div>
        <label>Afregningshed</label>
        <select>
            <option></option>
            <option></option>
            <option></option>
            <option></option>
            <option></option>
            <option></option>
        </select>
        <label>Km/Timer</label>
        <input type="number">
        <label>Beløb</label>
        <input type="number">
    </div>

</template>

<script>

    export default {

        methods: {
            saveChanges: function() {
                this.$emit('payment-amount')
            }
        }

    }
    
</script>