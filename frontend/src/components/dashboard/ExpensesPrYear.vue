<!-- Copyright (C) 2022 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <article class="expenses-pr-year">
        <fieldset>
            <year-selector @change="updateYear" />
        </fieldset>
        <div style="width: 40rem; height: auto;">
            <canvas :id="chart_id"></canvas>
        </div>
    </article>
</template>

<script>
import YearSelector from './YearSelector.vue'
import ajax from '../http/Http.js'
import Chart from 'chart.js/auto'

export default {
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
            const date_key = payment_list[0].node.date ? 'date' : 'paidDate' 
            const amount_key = payment_list[0].node.amount ? 'amount' : 'paidAmount' 
            
            let monthly_payments = [0,0,0,0,0,0,0,0,0,0,0,0]

            payment_list.forEach(payment => {
                const month_index = Number(payment.node[date_key].substring(5,7)) - 1
                const sum = new Number(monthly_payments[month_index])
                monthly_payments[month_index] = sum + Number(payment.node[amount_key])
            })
            return monthly_payments
        },
        renderChart: function(paymentdata) {
            this.chart_obj.data = {
                labels: ['jan', 'feb', 'mar', 'apr', 'maj', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'],
                datasets: [
                    {
                        label: 'Bevilligede ydelser',
                        data: paymentdata,
                        backgroundColor: 'hsl(222, 83%, 31%)',
                        borderWidth: 1
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
    }
</style>