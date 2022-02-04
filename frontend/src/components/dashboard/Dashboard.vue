<template>
    <article>
        <h1>Udgifter {{year}}</h1>
        <canvas id="chart1" width="400" height="400"></canvas>
        <p></p>

    </article>
    
</template>

<script>
import ajax from '../http/Http.js'
import Chart from 'chart.js/auto'

export default {
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
            console.log('got data', payment_list)
            const date_key = payment_list[0].node.date ? 'date' : 'paidDate' 
            const amount_key = payment_list[0].node.amount ? 'amount' : 'paidAmount' 
            
            let monthly_payments = [0,0,0,0,0,0,0,0,0,0,0,0]

            payment_list.forEach(payment => {
                const month_index = Number(payment.node[date_key].substring(5,7)) - 1
                const sum = new Number(monthly_payments[month_index])
                monthly_payments[month_index] = sum + Number(payment.node[amount_key])
            })
            console.log('got calc', monthly_payments)
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
                            backgroundColor: [
                                'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue',
                            ],
                            borderWidth: 1
                        },
                        {
                            label: 'Planlagte udgifter',
                            data: planned_payments,
                            backgroundColor: [
                                'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red'
                            ],
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
