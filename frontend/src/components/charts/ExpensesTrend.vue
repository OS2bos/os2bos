<!-- Copyright (C) 2022 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <article class="expenses-pr-year">
        <h2>Udviling i udgifter</h2>
        <canvas :id="chart_id"></canvas>
    </article>
</template>

<script>
import ajax from '../http/Http.js'
import Chart from 'chart.js/auto'

export default {
    data: function() {
        return {
            chart_id: 'chart-' + Math.floor(Math.random()*100),
            chart_obj: null
        }
    },
    methods: {
        setupChart: function(chart_id) {
            const ctx = document.getElementById(chart_id).getContext('2d')
            this.chart_obj = new Chart(ctx, {
                type: 'line',
                options: {
                    
                }
            })
        },
        fetchData: function() {
            let q = {
                query: `{
                    activities {
                        edges {
                            node {
                                totalGrantedThisYear,
                                totalGrantedPreviousYear,
                                totalGrantedNextYear,
                                totalExpectedThisYear,
                                totalExpectedPreviousYear,
                                totalExpectedNextYear
                            }
                        }
                    }
                }`
            }
            ajax.post('/graphql/', q)
            .then(res => {
                this.renderChart(this.sanitizeData(res.data.data.activities.edges))
            })          
        },
        sanitizeData: function(payments) {
            const this_year = Number(new Date().getUTCFullYear())
            const data_pack = {
                years: [this_year - 1, this_year, this_year + 1],
                granted: [0,0,0],
                expected: [0,0,0]
            }
            payments.forEach(payment => {
                data_pack.granted[0] += Number(payment.node.totalGrantedPreviousYear)
                data_pack.granted[1] += Number(payment.node.totalGrantedThisYear)
                data_pack.granted[2] += Number(payment.node.totalGrantedNextYear)
                data_pack.expected[0] += Number(payment.node.totalExpectedPreviousYear)
                data_pack.expected[1] += Number(payment.node.totalExpectedThisYear)
                data_pack.expected[2] += Number(payment.node.totalExpectedNextYear)
            })
            return data_pack
        },
        renderChart: function(data_pack) {
            this.chart_obj.data = {
                labels: data_pack.years,
                datasets: [
                    {
                        label: 'Bevilgede udgifter',
                        data: data_pack.granted,
                        fill: false,
                        borderColor: 'hsl(129, 83%, 31%)',
                        tension: 0.1
                    },
                    {
                        label: 'Forventede udgifter',
                        data: data_pack.expected,
                        fill: false,
                        borderColor: 'hsl(40, 83%, 62%)',
                        tension: 0.1
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
        width: 35rem;
    }
    .expenses-pr-year h2 {
        padding: .25rem 0 1.5rem;
    }
</style>