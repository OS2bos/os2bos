<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <div class="activity-summary">
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

        <div v-if="payment_plan.payment_type !== 'ONE_TIME_PAYMENT'">
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

</template>

<script>
import ActDisplayMixin from '../mixins/ActivityDisplayMixin.js'
import notify from '../notifications/Notify'
import PermissionLogic from '../mixins/PermissionLogic.js'

export default {
    
    mixins: [
        ActDisplayMixin,
        PermissionLogic
    ]

}
</script>

<style>

    .activity-summary {
        display: grid;
        grid-template-columns: repeat( auto-fill, minmax(10rem, 1fr) );
        gap: 2rem;
        background-color: var(--grey1);
        padding: 1.5rem 2rem 2rem;
    }

    .activity-summary dl {
        page-break-inside: avoid;
    }

    .activity-summary .label-EXPECTED {
        border: solid 1px hsl(var(--color3), 90%, 20%);
    }

</style>