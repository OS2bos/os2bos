<!-- Copyright (C) 2022 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <article>
        <h1>Udgifter {{year}}</h1>
        <div style="width: 40rem; height: auto;">
            <canvas id="chart1"></canvas>
        </div>
        <expenses-pr-activity />
        <expenses-pr-section />
    </article>
</template>

<script>
import ajax from '../http/Http.js'
import Chart from 'chart.js/auto'
import ExpensesPrActivity from './ExpensesPrActivity.vue'
import ExpensesPrSection from './ExpensesPrSection.vue'

export default {
    components: {
        ExpensesPrActivity,
        ExpensesPrSection
    },
    data: function() {
        return {
            planned_payments: [],
            actual_payments: [],
            year: 2022
        }
    },
    methods: {
        fetchPaymentsPerMonth: function() {
            let data = {
                query: `{
                    plannedPayments: payments(date_Gte: "${this.year}-01-01", date_Lte: "${this.year}-12-31") {
                        edges {
                            node {
                                date,
                                amount
                            }
                        }
                    },
                    actualPayments: payments(paidDate_Gte: "${this.year}-01-01", paidDate_Lte: "${this.year}-12-31") {
                        edges {
                            node {
                                paidAmount,
                                paidDate
                            }
                        }
                    }
                }`
            }
            ajax.post('/graphql/', data)
            .then(res => {
                const data = res.data.data
                this.planned_payments = this.calcMonthlyPayments(data.plannedPayments.edges)
                this.actual_payments = this.calcMonthlyPayments(data.actualPayments.edges)
                this.renderChart(this.actual_payments, this.planned_payments)
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
        renderChart: function(actual_payments, planned_payments) {

            const ctx = document.getElementById('chart1').getContext('2d');
            const myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['jan', 'feb', 'mar', 'apr', 'maj', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'],
                    datasets: [
                        {
                            label: 'Betalt',
                            data: actual_payments,
                            backgroundColor: 'hsl(222, 83%, 31%)',
                            borderWidth: 1
                        },
                        {
                            label: 'Planlagte udgifter',
                            data: planned_payments,
                            backgroundColor: 'hsl(40, 83%, 62%)',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            })
        }
    },
    created: function() {
        this.fetchPaymentsPerMonth()
    }
}
</script>
