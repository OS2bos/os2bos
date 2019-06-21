<template>

    <div class="payment-amount rows">

        <div class="payment-amount-fields">
            <h2>Beløb</h2>
            <label>Afregningshed</label>
            <div class="rows">
                <select v-model="type" style="margin-right: 1rem; min-width: 13rem;">
                    <option v-for="o in type_options" :key="o.key" :value="o.key">
                        {{ o.val }}
                    </option>
                </select>
                <select v-model="frequency" v-if="type !== 'ONE-TIME-PAYMENT'">
                    <option v-for="o in frequency_options" :key="o.key" :value="o.key">
                        {{ o.val }}
                    </option>
                </select>
            </div>
            <fieldset v-if="type === 'PER-HOUR-PAYMENT' || type === 'PER-DAY-PAYMENT' || type === 'PER-KM-PAYMENT'" class="rows">
                <div style="margin-right: .5rem;">
                    <label v-if="type === 'PER-HOUR-PAYMENT'">Timer</label>
                    <label v-if="type === 'PER-DAY-PAYMENT'">Døgn</label>
                    <label v-if="type === 'PER-KM-PAYMENT'">Kilometer</label>
                    <input v-model="units" type="number"> á
                </div>
                <div>
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
        <div>
            <button class="payment-schedule-btn" type="button" @click="paymentSchedule()">Betalingsplan</button>
        </div>
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
                units: 0,
                amount: 0
            }
        },
        methods: {
            saveChanges: function() {
                this.$emit('payment-amount')
            },
            paymentSchedule: function() {
                this.$router.push(`/paymentschedule/`)
            }
        }

    }
    
</script>

<style>

    .payment-amount .payment-plan {
        margin: 0 0 0 2em;
        background-color: var(--grey2);
        padding: 1rem;
    }

    .payment-amount.rows,
    .payment-amount .rows {
        display: flex;
        flex-flow: row nowrap;
    }

    .payment-amount input[type="text"] {
        width: 8rem;
    }

    .payment-schedule-btn {
        margin-left: 1rem;
    }

</style>