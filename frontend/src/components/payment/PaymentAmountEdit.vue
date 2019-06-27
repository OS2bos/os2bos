<template>

    <div class="payment-amount rows">

        <div class="payment-amount-fields">
            <h2>Beløb</h2>
            <label>Afregningshed</label>
            <div class="rows">
                <select v-model="entry.payment_type" style="margin-right: 1rem; min-width: 13rem;">
                    <option v-for="o in choices.type_options" :key="o.key" :value="o.key">
                        {{ o.val }}
                    </option>
                </select>
                <select v-model="entry.payment_frequency" v-if="entry.type !== 'ONE_TIME_PAYMENT'">
                    <option v-for="o in choices.frequency_options" :key="o.key" :value="o.key">
                        {{ o.val }}
                    </option>
                </select>
            </div>
            <fieldset v-if="entry.payment_type === 'PER_HOUR_PAYMENT' || entry.payment_type === 'PER_DAY_PAYMENT' || entry.payment_type === 'PER_KM_PAYMENT'" class="rows">
                <div style="margin-right: .5rem;">
                    <label v-if="entry.payment_type === 'PER_HOUR_PAYMENT'">Timer</label>
                    <label v-if="entry.payment_type === 'PER_DAY_PAYMENT'">Døgn</label>
                    <label v-if="entry.payment_type === 'PER_KM_PAYMENT'">Kilometer</label>
                    <input v-model="entry.payment_units" type="number"> á
                </div>
                <div>
                    <label>Takst</label>
                    <input v-model="entry.payment_amount" type="number"> kr
                </div>
            </fieldset>
            <fieldset v-else>
                <label>Beløb</label>
                <input v-model="entry.payment_amount" type="number"> kr
            </fieldset>
        </div>

        <payment-plan :amount="entry.payment_amount" :units="entry.payment_units" :type="entry.payment_type" :frequency="entry.payment_frequency" />
    </div>

</template>

<script>

    import PaymentPlan from './PaymentPlan.vue'

    export default {

        components: {
            PaymentPlan
        },
        props: [
            'paymentObj'
        ],
        data: function() {
            return {
                choices: {
                    type_options: [
                        {
                            key: 'ONE_TIME_PAYMENT',
                            val: 'Engangsudgift'
                        },
                        {
                            key: 'RUNNING_PAYMENT',
                            val: 'Fast beløb, løbende'
                        },
                        {
                            key: 'PER_HOUR_PAYMENT',
                            val: 'Takst pr. time'
                        },
                        {
                            key: 'PER_DAY_PAYMENT',
                            val: 'Takst pr. døgn'
                        },
                        {
                            key: 'PER_KM_PAYMENT',
                            val: 'Takst pr. kilometer'
                        }
                    ],
                    frequency_options: [
                        {
                            key: 'MONTHLY',
                            val: 'Månedligt'
                        },
                        {
                            key: 'WEEKLY',
                            val: 'Ugentligt'
                        },
                        {
                            key: 'DAILY',
                            val: 'Dagligt'
                        },
                    ],
                },
                entry: {
                    payment_type: 'RUNNING_PAYMENT', // default is running payment
                    payment_frequency: 'MONTHLY', // default is pr month
                    payment_units: 0,
                    payment_amount: 0
                }
            }
        },
        watch: {
            paymentObj: function() {
                this.entry = this.paymentObj
            },
            entry: {
                handler (newVal) {
                    this.$emit('update', this.entry)
                },
                deep: true
            }
        },
        created: function() {
            console.log(this.paymentObj)
            if (this.paymentObj) {
                this.entry = this.paymentObj
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