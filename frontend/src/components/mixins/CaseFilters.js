/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


export default {

    computed: {
        query: function() {
            return this.$route.query
        }
    },
    watch: {
        query: function() {
            this.update()
        }
    },
    methods: {
        update: function() {
            this.$store.dispatch('fetchCases', this.$route.query)
        },
        changeCpr: function(ev) {
            let cpr = ev.target.value.replace('-','')
            if (cpr.length === 10) {
                // Potential refactor: Maybe supply 'cpr_number' and 'case__cpr_number' as a function parameter.
                this.$route.query.cpr_number = cpr
                this.$route.query.case__cpr_number = cpr
                this.update()
            } else if (!cpr) {
                this.$route.query.cpr_number = ''
                this.$route.query.case__cpr_number = ''
                this.update()
            }
        },
        changeWorker: function(worker_id) {
            this.$route.query.case_worker = worker_id
            this.update()
        },
        changeTeam: function(team_id) {
            this.$route.query.team = team_id
            this.update()
        }
    }

}