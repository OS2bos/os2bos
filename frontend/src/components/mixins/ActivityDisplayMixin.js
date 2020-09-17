/* Copyright (C) 2020 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

import Type from '../activities/edittypes/Type.vue'
import Status from '../activities/edittypes/Status.vue'
import Activity from '../activities/edittypes/Activity.vue'
import Note from '../activities/edittypes/Note.vue'
import Fictional from '../payments/edittypes/Fictional.vue'

import PaymentType from '../payments/edittypes/PaymentType.vue'
import PayDateSingle from '../activities/edittypes/PayDateSingle.vue'
import PayDateSinglePeriodStart from '../activities/edittypes/PayDateSinglePeriodStart.vue'
import PayDateSinglePeriodEnd from '../activities/edittypes/PayDateSinglePeriodEnd.vue'
import PayDateSinglePeriodDisplay from '../activities/edittypes/PayDateSinglePeriodDisplay.vue'
import PayDateStart from '../activities/edittypes/PayDateStart.vue'
import PayDateEnd from '../activities/edittypes/PayDateEnd.vue'
import PaymentFrequency from '../payments/edittypes/PaymentFrequency.vue'

import CostType from '../payments/edittypes/CostType.vue'
import CostTypeFixed from '../payments/edittypes/CostTypeFixed.vue'
import CostTypeRate from '../payments/edittypes/CostTypeRate.vue'
import CostTypePerUnitDisplay from '../payments/edittypes/CostTypePerUnitDisplay.vue'
import PerUnitHistory from '../payments/PaymentPerUnitHistory.vue'
import PayPlanCalc from '../payments/PaymentPlanCalc.vue'

import PaymentReceiverType from '../payments/edittypes/PaymentReceiverType.vue'
import PaymentReceiverId from '../payments/edittypes/PaymentReceiverId.vue'
import PaymentReceiverName from '../payments/edittypes/PaymentReceiverName.vue'
import PaymentMethod from '../payments/edittypes/PaymentMethod.vue'
import PaymentMethodDetails from '../payments/edittypes/PaymentMethodDetails.vue'

export default {
    components: {
        Type,
        Status,
        Activity,
        Note,
        Fictional,
        PaymentType,
        PayDateSingle,
        PayDateSinglePeriodStart,
        PayDateSinglePeriodEnd,
        PayDateStart,
        PayDateEnd,
        PaymentFrequency,
        CostType,
        CostTypeFixed,
        CostTypeRate,
        CostTypePerUnitDisplay,
        PerUnitHistory,
        PayPlanCalc,
        PaymentReceiverType,
        PaymentReceiverId,
        PaymentReceiverName,
        PaymentMethod,
        PaymentMethodDetails,
        PayDateSinglePeriodDisplay
    },
    computed: {
        act: function() {
            return this.$store.getters.getActivity
        },
        payment_plan: function() {
            return this.$store.getters.getPaymentPlan
        },
        appropriation: function() {
            return this.$store.getters.getAppropriation
        }
    }
}