<!-- Copyright (C) 2022 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <article class="expenses-pr-section">
        <h2>Udgifter fordelt på paragraf</h2>
        <fieldset>
            <month-selector @change="updateMonth" />
            <year-selector @change="updateYear" />
        </fieldset>
        <div style="width: 20rem; height: auto;">
            <canvas :id="chart_id"></canvas>
        </div>
    </article>
</template>

<script>
import YearSelector from './YearSelector.vue'
import MonthSelector from './MonthSelector.vue'
import ajax from '../http/Http.js'
import { leadZero } from '../filters/Date.js'
import Chart from 'chart.js/auto'
import expensesMixin from './expensesMixin.js'

export default {
    mixins: [
        expensesMixin
    ],
    components: {
        YearSelector,
        MonthSelector
    },
    data: function() {
        return {
            chart_id: 'chart-' + Math.floor(Math.random()*100),
            chart_obj: null,
            year: Number(new Date().getUTCFullYear()),
            month: Number(new Date().getUTCMonth()) + 1
        }
    },
    methods: {
        fetchData: function() { 
            const q = {
                query: `{
                    payments (date_Gte: "${this.year}-${ leadZero(this.month) }-01", date_Lte: "${this.year}-${ leadZero(this.month + 1) }-01") {
                        totalCount,
                        edges {
                            node {
                                amount,
                                paymentSchedule {
                                    activity {
                                        appropriation {
                                            section {
                                                paragraph,
                                                text
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }`
            }

            ajax.post('/graphql/', q)
            .then(res => {
                this.renderChart(this.sanitizeData(res.data.data.payments.edges))
            })      
        },
        sanitizeData: function(edges) {
            let color_value = 80
            const data = {
                labels: [],
                backgroundColors: [],
                data: []
            }
            edges.forEach(e => {
                const section = e.node.paymentSchedule.activity.appropriation.section
                const paragraph = `${section.paragraph} ${section.text}`
                const idx = data.labels.findIndex(l => l === paragraph)
                const cost = Number(e.node.amount)
                if (idx < 0) {
                    data.labels.push(paragraph)
                    data.backgroundColors.push(`hsl(${ color_value },83%,31%)`)
                    color_value = this.incrementHue(color_value)
                    data.data.push(cost)
                } else {
                    data.data[idx] = data.data[idx] + cost
                }
            })
            return data
        },
        setupChart: function(chart_id) {
            const ctx = document.getElementById(chart_id).getContext('2d')
            this.chart_obj = new Chart(ctx, {
                type: 'doughnut',
                options: {
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            })
        },
        renderChart: function(data) {
            this.chart_obj.data = {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Udgifter fordelt på paragraf',
                        data: data.data,
                        backgroundColor: data.backgroundColors,
                        hoverOffset: 4
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
    .expenses-pr-section {
        display: inline-block;
        padding: 2rem 1rem;
        background-color: var(--grey1);
        width: auto;
    }
    .expenses-pr-section h2 {
        padding: .5rem 0;
        text-align: center;
    }
    .expenses-pr-section fieldset {
        display: flex;
        flex-flow: row nowrap;
        justify-content: center;
        gap: 1rem;
    }
</style>