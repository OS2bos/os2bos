<!-- Copyright (C) 2022 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <article class="expenses-pr-year">
        <header>
            <h2>Bevilligede ydelser</h2>
            <fieldset>
                <year-selector @change="updateYear" />
            </fieldset>
        </header>
        <canvas :id="chart_id"></canvas>
    </article>
</template>

<script>
import YearSelector from './YearSelector.vue'
import ajax from '../http/Http.js'
import Chart from 'chart.js/auto'
import expensesMixin from './expensesMixin.js'

export default {
    mixins: [
        expensesMixin
    ],
    components: {
        YearSelector
    },
    data: function() {
        return {
            chart_id: 'chart-' + Math.floor(Math.random()*100),
            chart_obj: null,
            year: Number(new Date().getUTCFullYear())
        }
    },
    methods: {
        setupChart: function(chart_id) {
            const ctx = document.getElementById(chart_id).getContext('2d')
            this.chart_obj = new Chart(ctx, {
                type: 'bar',
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            })
        },
        fetchData: function() {
            let q = {
                query: `{
                    payments(date_Gte: "${this.year}-01-01", date_Lte: "${this.year}-12-31") {
                        edges {
                            node {
                                date,
                                amount
                            }
                        }
                    }
                }`
            }
            ajax.post('/graphql/', q)
            .then(res => {
                this.renderChart(this.calcMonthlyPayments(res.data.data.payments.edges))
            })          
        },
        calcMonthlyPayments: function(payment_list) {
            let monthly_payments = [0,0,0,0,0,0,0,0,0,0,0,0]

            payment_list.forEach(payment => {
                const month_index = Number(payment.node.date.substring(5,7)) - 1
                const sum = new Number(monthly_payments[month_index])
                monthly_payments[month_index] = sum + Number(payment.node.amount)
            })
            return monthly_payments
        },
        renderChart: function(paymentdata) {
            this.chart_obj.data = {
                labels: ['jan', 'feb', 'mar', 'apr', 'maj', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'],
                datasets: [
                    {
                        label: `Bevilligede ydelser ${this.year}`,
                        data: paymentdata,
                        backgroundColor: 'hsl(40, 83%, 62%)',
                        borderWidth: 0
                    }
                ]
            }
            this.chart_obj.update()
        }
    },
    mounted: function() {
        this.setupChart(this.chart_id)
        this.fetchData()
    }
}
</script>

<style>
    .expenses-pr-year {
        display: block;
        padding: 2rem 2rem 0;
        background-color: var(--grey1);
        margin: 0;
        max-width: auto;
        width: 35rem;
    }
    .expenses-pr-year header {
        display: flex;
        flex-flow: row nowrap;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    .expenses-pr-year fieldset {
        margin: 0;
    }
    .expenses-pr-year h2 {
        padding: .25rem 0 0;
    }
</style>