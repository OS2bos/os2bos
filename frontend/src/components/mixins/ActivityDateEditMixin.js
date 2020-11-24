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
                // Ved ny følgeydelse (ikke forventning), returner startdato for hovedydelse
                return epoch2DateStr(this.getMainActStartDate())
            }
            if (this.mode === 'clone' && this.act.activity_type !== 'MAIN_ACTIVITY') {
                // Ved forvenintning til følgeydelse, slet kopieret startdato og returner startdato for hovedydelse
                this.$store.commit('setActivityProperty', {prop: 'start_date', val: null})
                return epoch2DateStr(this.getMainActStartDate())
            }
            if (this.mode === 'clone' && this.act.activity_type === 'MAIN_ACTIVITY') {
                // Ved forventning til hovedydelse, slet kopieret startdato
                this.$store.commit('setActivityProperty', {prop: 'start_date', val: null})
            }
            // Ellers sæt begrænsning for startdato 10 år tilbage
            return tenYearsAgo()
        },
        endDateSet: function() {
            if (this.act.activity_type !== 'MAIN_ACTIVITY' && this.mode !== 'clone') {
                return epoch2DateStr(this.getMainActEndDate())
            }
            if (this.mode === 'clone' && this.act.activity_type !== 'MAIN_ACTIVITY') {
                this.$store.commit('setActivityProperty', {prop: 'end_date', val: null})
                return epoch2DateStr(this.getMainActEndDate())
            }
            if (this.mode === 'clone' && this.act.activity_type === 'MAIN_ACTIVITY') {
                this.$store.commit('setActivityProperty', {prop: 'end_date', val: null})
            }
            return inEighteenYears()
        }
    },
    methods: {
        displayDate: function(dt) {
            return json2jsDate(dt)
        },
        getMainActStartDate: function() {
            let start_date
            if (this.appropriation.granted_from_date) {
                start_date = this.appropriation.granted_from_date
            } else if (this.appropriation.main_activity && this.appropriation.main_activity.start_date) {
                start_date = this.appropriation.main_activity.start_date
            } else {
                start_date = null
            }
            return start_date
        },
        getMainActEndDate: function() {
            let end_date
            if (this.appropriation.granted_to_date) {
                end_date = this.appropriation.granted_to_date
            } else if (this.appropriation.main_activity && this.appropriation.main_activity.end_date) {
                end_date = this.appropriation.main_activity.end_date
            } else {
                end_date = null
            }
            return end_date
        }
    }
}