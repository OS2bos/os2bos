<!-- Copyright (C) 2022 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <section class="dashboard">
        <h1>Økonomisk overblik</h1>
        <div class="dashboard-grid">
            <expenses-pr-year />
            <expenses-pr-section />
            <expenses-pr-activity />
            <expenses-trend />
        </div>
    </section>
</template>

<script>
import ExpensesPrActivity from './ExpensesPrActivity.vue'
import ExpensesPrSection from './ExpensesPrSection.vue'
import ExpensesPrYear from './ExpensesPrYear.vue'
import ExpensesTrend from './ExpensesTrend.vue'

export default {
    components: {
        ExpensesPrActivity,
        ExpensesPrSection,
        ExpensesPrYear,
        ExpensesTrend
    }
}
</script>

<style>
    .dashboard {
        width: 67.5rem;
        margin: 0 auto;
    }
    .dashboard-grid {
        display: flex;
        gap: 1rem;
        flex-flow: row wrap;
        justify-content: flex-start;
    }
    .dashboard-grid > * {
        flex: 1 0 auto;
    }
</style>
