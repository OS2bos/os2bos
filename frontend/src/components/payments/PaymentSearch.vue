<template>
    
    <div class="payment-search">

        <div class="payment-search-list">
            <h1>Betalinger</h1>
            <table v-if="payments.length > 0">
                <thead>
                    <tr>
                        <th>Nøgle</th>
                        <th>Beløb</th>
                        <th>Betalingsdato</th>
                        <th>Betalt</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="p in payments" :key="p.id">
                        <td><router-link :to="`/payment/${ p.id }/`">Betaling {{ p.id }}</router-link></td>
                        <td>{{ p.amount }}</td>
                        <td>{{ p.date }}</td>
                        <td>{{ p.paid }}</td>
                    </tr>
                </tbody>
            </table>
            <p v-if="payments.length < 1">
                Kunne ikke finde nogen sager
            </p>
            <button class="more">Vis flere <i class="material-icons">keyboard_arrow_down</i></button>
        </div>

        <div class="payment-search-filters">
            <h2>Filtre</h2>
            <form>
                <fieldset>
                    <label>Betalingsnøgle</label>
                    <input @input="changeId()" type="text" v-model="field_id">
                </fieldset>
                <fieldset>
                    <label>Kontostreng</label>
                    <input @input="changeAccount()" type="text" v-model="field_account">
                </fieldset>
            </form>
        </div>

    </div>

</template>

<script>

    export default {
        
        data: function() {
            return {
                field_id: null,
                field_account: null
            }
        },
        computed: {
            payments: function() {
                return this.$store.getters.getPayments
            }
        },
        methods: {
            update: function() {
                this.$store.dispatch('fetchPayments', this.$route.query)
            },
            changeId: function() {
                this.$route.query.id = this.field_id
                this.update()
            },
            changeAccount: function() {
                this.$route.query.account = this.field_account
                this.update()
            }
        },
        created: function() {
            this.update()
        }

    }

</script>

<style>

    .payment-search {
        padding: 2rem;
        display: flex;
        flex-flow: row nowrap;
    }

    .payment-search-list {
        order: 2;
    }

    .payment-search-list .more .material-icons {
        margin: 0;
    }

    .payment-search-filters {
        order: 1;
        background-color: var(--grey1);
        padding: 1rem;
        margin-right: 2rem;
    }

    .payment-search-filters h2,
    .payment-search-filters form {
        padding: 0;
    }

</style>