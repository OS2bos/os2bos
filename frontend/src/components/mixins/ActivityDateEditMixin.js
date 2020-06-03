/* Copyright (C) 2020 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

import { epoch2DateStr, tenYearsAgo, inEighteenYears, json2jsDate } from '../filters/Date.js'

export default {
    computed: {
        act: function() {
            return this.$store.getters.getActivity
        },
        appropriation: function() {
            return this.$store.getters.getAppropriation
        },
        startDateSet: function() {
            if (this.act.activity_type !== 'MAIN_ACTIVITY' && this.mode !== 'clone') {
                return epoch2DateStr(this.appropriation.granted_from_date)
            }
            if (this.mode === 'clone' && this.act.activity_type !== 'MAIN_ACTIVITY') {
                this.act.start_date = null
                return epoch2DateStr(this.appropriation.granted_from_date)
            }
            if (this.mode === 'clone' && this.act.activity_type === 'MAIN_ACTIVITY') {
                this.act.start_date = null
            }
            return tenYearsAgo()
        },
        endDateSet: function() {
            if (this.act.activity_type !== 'MAIN_ACTIVITY' && this.mode !== 'clone') {
                return epoch2DateStr(this.appropriation.granted_to_date)
            }
            if (this.mode === 'clone' && this.act.activity_type !== 'MAIN_ACTIVITY') {
                this.act.end_date = null
                return epoch2DateStr(this.appropriation.granted_to_date)
            }
            if (this.mode === 'clone' && this.act.activity_type === 'MAIN_ACTIVITY') {
                this.act.end_date = null
            }
            return inEighteenYears()
        }
    },
    methods: {
        displayDate: function(dt) {
            return json2jsDate(dt)
        }
    }
}