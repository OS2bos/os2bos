<!-- Copyright (C) 2022 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <article>
        <h1>Økonomisk overblik</h1>
        <div class="dashboard-grid">
            <expenses-pr-year />
            <expenses-pr-activity />
            <expenses-pr-section />
        </div>
    </article>
</template>

<script>
import ExpensesPrActivity from './ExpensesPrActivity.vue'
import ExpensesPrSection from './ExpensesPrSection.vue'
import ExpensesPrYear from './ExpensesPrYear.vue'

export default {
    components: {
        ExpensesPrActivity,
        ExpensesPrSection,
        ExpensesPrYear
    }
}
</script>

<style>
    .dashboard-grid {
        display: grid;
        gap: 1rem;
        grid-template-columns: 1fr 1fr;
        grid-template-rows: 1fr 1fr;
    }
    .dashboard-grid *:first-child {
        grid-area: 1 / 1 / 2 / 3;
    }
</style>