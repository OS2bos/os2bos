<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <div class="payment-modal">

        <button @click="openPaymentDiag">Betaling #{{ this.pId }}</button>

        <div class="modal-mask" v-if="show_modal">
            <div class="modal-wrapper">

                <payment-component @close="closeDiag()" @update="$emit('update')"/>
                
            </div>
        </div>    

    </div>

</template>

<script>

    import PaymentComponent from './Payment.vue'

    export default {
        
        components: {
            PaymentComponent
        },
        props: [
            'pId'
        ],
        data: function() {
            return {
                show_modal: false
            }
        },
        methods: {
            openPaymentDiag: function() {
                this.$route.params.payId = this.pId
                this.show_modal = true
            },
            closeDiag: function() {
                this.show_modal = false
            }
        }

    }

</script>
