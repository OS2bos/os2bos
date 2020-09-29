<template>
    
    <form @submit.prevent="savePayment" class="payment-create modal-form">
        <modal-dialog @closedialog="closeDiag">
            
            <h2 slot="header">Opret ny betaling</h2>

            <div slot="body">

                <fieldset>
                    <label for="field-payment-planned-amount" class="required">Beløb</label>
                    <input type="number" v-model="payment.amount" step="0.01" required id="field-payment-planned-amount"> kr
                </fieldset>

                <fieldset>
                    <label for="field-payment-planned-date" class="required">Betalingsdato</label>
                    <input type="date" v-model="payment.date" required id="field-payment-planned-date">
                </fieldset>

                <error />

            </div>
            
            <div slot="footer">
                <button id="submit-planned-payment-btn" type="submit">Gem</button>
                <button type="button" @click="closeDiag">Annullér</button>
            </div>

        </modal-dialog>
    </form>

</template>

<script>
import ModalDialog from '../../dialog/Dialog.vue'
import Error from '../../forms/Error.vue'
import axios from '../../http/Http.js'

export default {
    components: {
        ModalDialog,
        Error
    },
    props: [
        'plan'
    ],
    data: function() {
        return {
            payment: {
                amount: null,
                date: null,
                paid: false
            }
        }
    },
    computed: {
        payment_plan: function() {
            return this.plan
        }
    },
    methods: {
        closeDiag: function() {
            this.$emit('closedialog')
            this.$store.commit('clearErrors')
        },
        savePayment: function() {
            
            let p = this.payment
            p.payment_schedule = this.payment_plan.id
            p.recipient_type = this.payment_plan.recipient_type
            p.recipient_name = this.payment_plan.recipient_name
            p.payment_method = this.payment_plan.payment_method
            if (this.payment_plan.recipient_id) {
                p.recipient_id = this.payment_plan.recipient_id
            }

            axios.post(`/payments/`, p)
            .then(() => {
                this.$emit('paymentsaved')
                this.closeDiag()
            })
            .catch(err => this.$store.dispatch('parseErrorOutput', err))
        }
    }
    
}
</script>