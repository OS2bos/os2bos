<template>

    <div class="payment-amount">

        <div>
            <label>Afregningshed</label>
            <div style="display: flex; flex-flow: row nowrap;">
                <select v-model="type" style="margin-right: 1rem; min-width: 13rem;">
                    <option v-for="o in type_options" :key="o.key" :value="o.key">
                        {{ o.val }}
                    </option>
                </select>
                <select v-model="frequency">
                    <option v-for="o in frequency_options" :key="o.key" :value="o.key">
                        {{ o.val }}
                    </option>
                </select>
            </div>
            <fieldset v-if="type === 'PER-HOUR-PAYMENT' || type === 'PER-DAY-PAYMENT' || type === 'PER-KM-PAYMENT'">
                <div>
                    <label v-if="type === 'PER-HOUR-PAYMENT'">Timer</label>
                    <label v-if="type === 'PER-DAY-PAYMENT'">Døgn</label>
                    <label v-if="type === 'PER-KM-PAYMENT'">Kilometer</label>
                    <input v-model="units" type="number"> <span></span>
                    <label>Takst</label>
                    <input v-model="amount" type="number"> kr
                </div>
            </fieldset>
            <fieldset v-else>
                <label>Beløb</label>
                <input v-model="amount" type="number"> kr
            </fieldset>
        </div>

        <payment-plan :amount="amount" :units="units" :type="type" :frequency="frequency" />

    </div>

</template>

<script>

    import PaymentPlan from './PaymentPlan.vue'

    export default {

        components: {
            PaymentPlan
        },
        data: function() {
            return {
                type: 'RUNNING-PAYMENT', // default is running payment
                type_options: [
                    {
                        key: 'ONE-TIME-PAYMENT',
                        val: 'Engangsudgift'
                    },
                    {
                        key: 'RUNNING-PAYMENT',
                        val: 'Fast beløb, løbende'
                    },
                    {
                        key: 'PER-HOUR-PAYMENT',
                        val: 'Takst pr. time'
                    },
                    {
                        key: 'PER-DAY-PAYMENT',
                        val: 'Takst pr. døgn'
                    },
                    {
                        key: 'PER-KM-PAYMENT',
                        val: 'Takst pr. kilometer'
                    }
                ],
                frequency: 'PAY-EVERY-MONTH', // default is pr month
                frequency_options: [
                    {
                        key: 'PAY-EVERY-MONTH',
                        val: 'Månedligt'
                    },
                    {
                        key: 'PAY-EVERY-WEEK',
                        val: 'Ugentligt'
                    },
                    {
                        key: 'PAY-EVERY-DAY',
                        val: 'Dagligt'
                    },
                ],
                units: null,
                amount: null
            }
        },
        methods: {

            saveChanges: function() {
                this.$emit('payment-amount')
            }
        }

    }
    
</script>

<style>

    .payment-amount {
        display: flex;
        flex-flow: row nowrap;
    }

    .payment-amount .payment-plan {
        margin: 0 0 0 2em;
    }

</style>