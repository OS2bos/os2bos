/* Copyright (C) 2020 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

import { epoch2DateStr, tenYearsAgo, inEighteenYears, json2jsDate } from '../filters/Date.js'

export default {
    computed: {
        acts: function() {
            return this.$store.getters.getActivities
        },
        main_activities: function() {
            if (this.acts) {
                return this.acts.filter(function(act) {
                    return act.activity_type === 'MAIN_ACTIVITY'
                })
            }
        },
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
            let acts = this.sortMainActs()
            return this.getBestDate(acts,'start')
        },
        getMainActEndDate: function() {
            let acts = this.sortMainActs()
            return this.getBestDate(acts,'end')
        },
        getBestDate(arr, criteria) {
            if (arr.length) {
                let best_date = null
                if (criteria === 'start') {
                    best_date = arr[0].start_date
                } else {
                    best_date = arr[arr.length - 1].end_date
                }
                return best_date
            }
        },
        sortMainActs() {
            // Sort mainActs list by start date
            return this.main_activities.sort(function(a,b) {
                const a_start_date = new Date(a.start_date).getTime(),
                    b_start_date = new Date(b.start_date).getTime()
                if (a_start_date > b_start_date) {
                    return 1
                } else if (b_start_date > a_start_date) {
                    return -1
                } else {
                    return 0
                }
            })
        }
    }
}
