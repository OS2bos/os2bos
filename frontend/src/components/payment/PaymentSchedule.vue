<template>

    <section class="payment_schedule">
      <div class="row">
        <div class="column">
          <label>Vælg år</label>
          <select>
            <option value="2019">2019</option>
            <option value="2018">2018</option>
            <option value="2017">2017</option>
          </select>
        </div>
        <div class="column"></div>
      </div>
        <table>
            <thead>
                <tr>
                    <th>Måned</th>
                    <th>Beløb</th>
                    <th>Betalt</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="p in paymentsObj" :key="p.id">
                    <td>{{ displayDate(p.date) }}</td>
                    <td>{{ p.amount }}</td>
                    <td>
                        <div v-if="p.paid === 'true'">Betalt</div>
                        <div v-if="p.paid === 'false'">Ikke betalt</div>
                    </td>
                </tr>
            </tbody>
        </table>
    </section>

</template>

<script>

    import { json2js } from '../filters/Date.js'

    export default {

        props: [
            'paymentsObj'
        ],

        methods: {
            displayDate: function(dt) {
                return json2js(dt)
            }
        }
    }
</script>

<style>

    .payment_schedule {
        margin: 1rem;
    }

    .payment_schedule-header {
        display: flex;
        flex-flow: row nowrap;
        justify-content: flex-start;
        align-items: center;
    }

</style>
