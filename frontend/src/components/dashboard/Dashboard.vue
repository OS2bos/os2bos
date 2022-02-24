<template>
    <article>
        <h1>Økonomioverblik</h1>
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
                console.log('got data', data)
                this.planned_payments = this.calcMonthlyPayments(data.plannedPayments.edges)
                this.actual_payments = this.calcMonthlyPayments(data.actualPayments.edges)
                this.renderChart(this.actual_payments, this.planned_payments)
            })
                    
        },
        calcMonthlyPayments: function(payment_list) {
            let monthly_payments = [0,0,0,0,0,0,0,0,0,0,0,0]
            payment_list.forEach(payment => {
                const month = Number(payment.node.date.substring(5,2))
                console.log('got a month', month)
            })
            return monthly_payments
        },
        renderChart: function(paymentdata) {

            const ctx = document.getElementById('chart1').getContext('2d');
            const myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['jan', 'feb', 'mar', 'apr', 'maj', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'],
                    datasets: [
                        {
                            label: 'Planlagte udgifter',
                            data: [12, 19, 3, 5, 2, 3, 12, 19, 3, 5, 2, 3],
                            backgroundColor: [
                                'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red', 'red'
                            ],
                            borderWidth: 1
                        },
                        {
                            label: 'Betalt',
                            data: [3,1,4,3,6,3,13,3,9,2,13,8],
                            backgroundColor: [
                                'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue', 'blue',
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
