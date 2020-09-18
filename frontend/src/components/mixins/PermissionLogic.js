/* Copyright (C) 2020 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

import { epoch2DateStr } from '../filters/Date.js'

export default {
    computed: {
        user: function() {
            return this.$store.getters.getUser
        },
        current_act: function() {
            return this.$store.getters.getActivity
        },
        payments: function() {
            return this.$store.getters.getPayments
        },
        user_can_edit: function() {
            // Returns true if user of a given profile type has editing permissions
            switch(this.user.profile) {
                case 'admin':
                    return true
                case 'workflow_engine':
                    return true
                case 'grant':
                    return true
                case 'edit':
                    return true
                case 'readonly':
                    return false
                default:
                    return false
            }
        },
        can_create_payment: function() {
            if (this.$store.state.payment.payment_plan.payment_type === 'INDIVIDUAL_PAYMENT' && this.current_act.status !== 'GRANTED' && this.user.profile !== 'readonly') {
                return true
            } else {
                return false
            }
        },
        can_edit_payment: function() {
            if (this.$store.state.payment.payment_plan.payment_type === 'INDIVIDUAL_PAYMENT' && this.current_act.status !== 'GRANTED' && this.user.profile !== 'readonly') {
                return true
            } else if (this.user.profile === 'workflow_engine' && this.current_act.status !== 'GRANTED') {
                return true  
            } else if (this.user.profile === 'admin' && this.current_act.status !== 'GRANTED') {
                return true  
            } else {
                return false
            }
        },
        can_delete_payment: function() {
            if (this.$store.state.payment.payment_plan.payment_type === 'INDIVIDUAL_PAYMENT' && this.current_act.status !== 'GRANTED' && this.user.profile !== 'readonly') {
                return true
            } else {
                return false
            }
        }
    },
    methods: {
        is_individual_payment_type: function(payment_plan) {
            if (payment_plan.payment_type === 'INDIVIDUAL_PAYMENT') {
                return true
            } else {
                return false
            }
        },
        is_payable: function(payment) {
            if (payment.activity__status === 'GRANTED') {
                if (this.user.profile === 'workflow_engine' || this.user.profile === 'admin') {
                    return true
                } else if (payment.is_payable_manually && !payment.paid && this.user.profile !== 'readonly' && payment.payment_method !== 'SD' && payment.payment_method !== 'CASH') {
                    return true
                } else {
                    return false
                }
            } else {
                return false
            }
        },
        warn_edit_payment: function(payment) {
            if (payment.payment_method === 'SD' || payment.payment_method === 'CASH') {
                let two_days_ago = epoch2DateStr(new Date().setDate(new Date().getDate() - 2))
                if (two_days_ago < payment.date) {
                    return 'OBS: Rettede beløb og dato vil automatisk blive overskrevet, hvis planlagt betalingsdato er i fremtiden.'
                }
            }
        }
    }
}