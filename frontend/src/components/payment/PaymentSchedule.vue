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
                <tr>
                    <td>Januar</td>
                    <td>Ingen betaling</td>
                    <td>Nej</td>
                </tr>
                <tr>
                    <td>Februar</td>
                    <td></td>
                    <td></td>
                </tr>
                <tr>
                    <td>Marts</td>
                    <td></td>
                    <td></td>
                </tr>
                <tr>
                    <td>April</td>
                    <td></td>
                    <td></td>
                </tr>
                <tr>
                    <td>Maj</td>
                    <td></td>
                    <td></td>
                </tr>
                <tr>
                    <td>Juni</td>
                    <td></td>
                    <td></td>
                </tr>
                <tr>
                    <td>Juli</td>
                    <td></td>
                    <td></td>
                </tr>
                <tr>
                    <td>August</td>
                    <td></td>
                    <td></td>
                </tr>
                <tr>
                    <td>September</td>
                    <td></td>
                    <td></td>
                </tr>
                <tr>
                    <td>Oktober</td>
                    <td></td>
                    <td></td>
                </tr>
                <tr>
                    <td>November</td>
                    <td></td>
                    <td></td>
                </tr>
                <tr>
                    <td>December</td>
                    <td></td>
                    <td></td>
                </tr>
            </tbody>
        </table>
    </section>

</template>

<script>

    export default {

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
