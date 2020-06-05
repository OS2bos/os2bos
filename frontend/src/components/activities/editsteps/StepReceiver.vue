<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <div class="act-create-step">
        <h2>Beløbsmodtager</h2>
        <payment-receiver-type :editable="true" />
        <template v-if="payment_plan.recipient_type">
            <payment-service-provider v-if="payment_plan.recipient_type === 'COMPANY'" />
            
            <cpr-look-up 
                v-if="payment_plan.recipient_type === 'PERSON'" 
                :cpr.sync="recipient_id" 
                :name.sync="recipient_name" />

            <payment-internal-receiver v-if="payment_plan.recipient_type === 'INTERNAL'" /> 

            <payment-receiver-id 
                :editable="true" 
                v-if="payment_plan.recipient_type && payment_plan.recipient_type !== 'PERSON'" />
            
            <payment-receiver-name 
                :editable="true"
                v-if="payment_plan.recipient_type && payment_plan.recipient_type === 'COMPANY'" />

            <payment-method :editable="true" v-if="payment_plan.recipient_type === 'PERSON'" />

            <payment-method-details :editable="true" v-if="payment_plan.payment_method === 'SD'" />
        </template>
    </div>

</template>

<script>
import PaymentReceiverType from '../../payments/edittypes/PaymentReceiverType.vue'
import PaymentServiceProvider from '../../payments/edittypes/PaymentServiceProvider.vue'
import CprLookUp from '../../forms/CprLookUp.vue'
import PaymentReceiverId from '../../payments/edittypes/PaymentReceiverId.vue'
import PaymentReceiverName from '../../payments/edittypes/PaymentReceiverName.vue'
import PaymentMethod from '../../payments/edittypes/PaymentMethod.vue'
import PaymentMethodDetails from '../../payments/edittypes/PaymentMethodDetails.vue'
import PaymentInternalReceiver from '../../payments/edittypes/PaymentInternalReceiverName.vue'

export default {
    components: {
        PaymentReceiverType,
        PaymentServiceProvider,
        PaymentReceiverId,
        PaymentReceiverName,
        PaymentMethod,
        PaymentMethodDetails,
        CprLookUp,
        PaymentInternalReceiver
    },
    computed: {
        payment_plan: function() {
            return this.$store.getters.getPaymentPlan
        },
        recipient_id: {
            get: function() {
                return this.$store.getters.getPaymentPlanProperty('recipient_id')
            },
            set: function(new_val) {
                this.$store.commit('setPaymentPlanProperty', {
                    prop: 'recipient_id',
                    val: new_val
                })
            }
        },
        recipient_name: {
            get: function() {
                return this.$store.getters.getPaymentPlanProperty('recipient_name')
            },
            set: function(new_val) {
                this.$store.commit('setPaymentPlanProperty', {
                    prop: 'recipient_name',
                    val: new_val
                })
            }
        }

    }
}
</script>