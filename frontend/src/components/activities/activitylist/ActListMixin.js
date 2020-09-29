/* Copyright (C) 2020 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

import { activityId2name, displayStatus } from '../../filters/Labels.js'
import { cost2da } from '../../filters/Numbers.js'
import { json2jsDate } from '../../filters/Date.js'

export default {
    computed: {
        selectedValue: function(){
            return this.$store.getters.getSelectedCostCalc
        }
    },
    methods: {
        statusLabel: function(status) {
            return displayStatus(status)
        },
        displayDigits: function(num) {
            return cost2da(num)
        },
        displayDate: function(dt) {
            return json2jsDate(dt)
        },
        activityId2name: function(id) {
            return activityId2name(id)
        },
        displayCost: function(act, column, is_meta) {
            if (is_meta) {
                if (column === 'granted') {
                    if (act.approved !== 0) {
                        return `${ this.displayDigits(act.approved) } kr`
                    }
                } else {
                    if (act.expected !== act.approved) {
                        return `${ this.displayDigits(act.expected) } kr`
                    }
                }
            } else {
                if (column === 'granted') {
                    if (act.status === 'GRANTED' && this.selectedValue === '1') {
                        return `${ this.displayDigits(act.total_granted_this_year) } kr`
                    }
                    if (act.status === 'GRANTED' && this.selectedValue === '2') {
                        return `${ this.displayDigits(act.total_cost_full_year) } kr`
                    }
                    if (act.status === 'GRANTED' && this.selectedValue === '3') {
                        return `${ this.displayDigits(act.total_cost) } kr`
                    }
                } else {
                    if (act.total_expected_this_year === 0 || act.total_expected_this_year !== act.total_granted_this_year && this.selectedValue === '1') {
                        return `${ this.displayDigits(act.total_expected_this_year) } kr`
                    }
                    if (act.total_expected_this_year === 0 || act.total_expected_this_year !== act.total_granted_this_year && this.selectedValue === '2') {
                        return `${ this.displayDigits(act.total_cost_full_year) } kr`
                    }
                    if (act.total_expected_this_year === 0 || act.total_expected_this_year !== act.total_granted_this_year && this.selectedValue === '3') {
                        return `${ this.displayDigits(act.total_cost) } kr`
                    }
                }
            }
        }
    }
}