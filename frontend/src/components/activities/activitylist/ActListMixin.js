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
    data: function() {
        return {
            this_year: String(new Date().getUTCFullYear()),
            next_year: String(new Date().getUTCFullYear() + 1),
            previous_year: String(new Date().getUTCFullYear() - 1),
        }
    },
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
            
            
                if (column === 'granted') {
                    if (this.selectedValue === this.previous_year) {
                        return `${ this.displayDigits(act.total_granted_previous_year) } kr`
                    }
                    if (this.selectedValue === this.this_year) {
                        return `${ this.displayDigits(act.total_granted_this_year) } kr`
                    }
                    if (this.selectedValue === this.next_year) {
                        return `${ this.displayDigits(act.total_granted_next_year) } kr`
                    }
                } else {
                    if (this.selectedValue === this.previous_year) {
                        return `${ this.displayDigits(act.total_expected_previous_year) } kr`
                    }
                    if (this.selectedValue === this.this_year) {
                        return `${ this.displayDigits(act.total_expected_this_year) } kr`
                    }
                    if (this.selectedValue === this.next_year) {
                        return `${ this.displayDigits(act.total_expected_next_year) } kr`
                    }
                }
            
        }
    }
}