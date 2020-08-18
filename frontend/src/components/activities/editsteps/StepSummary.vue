<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <div class="act-create-step act-create-step-summary">
        <h2 style="padding: 0 0 .5rem;">Opsummering</h2>

        <div class="act-create-summary">
            <div>
                <status :editable="false" />
                <fictional :editable="false" />
                <activity :editable="false" />
            </div>
            
            <div>
                <payment-type :editable="false" />
                <template v-if="payment_plan.payment_type === 'ONE_TIME_PAYMENT'">
                    <pay-date-single :editable="false" />
                    <pay-date-single-period-display />
                </template>
            </div>

            <div v-if="payment_plan.payment_type === 'RUNNING_PAYMENT'">
                <pay-date-start :editable="false" />
                <pay-date-end :editable="false" />
            </div>
     
            <payment-frequency :editable="false" v-if="!is_individual_payment_type(payment_plan)" />
            
            <div v-if="!is_individual_payment_type(payment_plan)">
                <cost-type :editable="false" />
                <template v-if="payment_plan.payment_cost_type === 'FIXED'">
                    <cost-type-fixed :editable="false" />
                </template>
                <template v-if="payment_plan.payment_cost_type === 'GLOBAL_RATE'">
                    <cost-type-rate :editable="false" />
                </template>
                <template v-if="payment_plan.payment_cost_type === 'PER_UNIT'">
                    <cost-type-per-unit-display :editable="false" />
                </template>
            </div>

            <div>
                <payment-receiver-type :editable="false" />
                <payment-receiver-id :editable="false" />
                <payment-receiver-name :editable="false" />
            </div>
               
            <div>
                <payment-method :editable="false" />
                <payment-method-details :editable="false" />
            </div>
   
            <note :editable="false" />
        </div>

        <error />

        <fieldset style="margin-bottom: 0; padding-bottom: 2rem;">
            <hr>
            <input type="submit" id="activity-submit" @click="save" style="margin-right: .5rem;" value="Gem">
            <button @click="cancel">Annuller</button>
        </fieldset>
    </div>
</template>

<script>
import ActDisplayMixin from '../../mixins/ActivityDisplayMixin.js'
import Error from '../../forms/Error.vue'
import notify from '../../notifications/Notify'
import PermissionLogic from '../../mixins/PermissionLogic.js'

export default {
    
    mixins: [
        ActDisplayMixin,
        PermissionLogic
    ],
    components: {
        Error
    },
    computed: {
        act: function() {
            return this.$store.getters.getActivity
        }
    },
    methods: {
        save: function() {
            this.$emit('save')
        },
        cancel: function() {
            this.$emit('cancel')
        }
    }

}
</script>

<style>

    .act-create-summary {
        display: grid;
        grid-template-columns: repeat( auto-fill, minmax(10rem, 1fr) );
        gap: 2rem;
    }

    .act-create-summary dl {
        page-break-inside: avoid;
    }

</style>