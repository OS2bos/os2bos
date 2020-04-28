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
          this.$store.dispatch('fetchAppropriations', this.$route.query)
      },
      changeSection: function(section_id) {
        if (this.$route.query.section != section_id) { // Only update if choice is different
            this.$route.query.section = section_id
            this.update()
        }
      },
      changeMainAct: function(main_activity_id) {
        if (this.$route.query.main_activity__details__id != main_activity_id) { // Only update if choice is different
            this.$route.query.main_activity__details__id = main_activity_id
            this.update()
        }
      },
      changeCpr: function(ev) {
          let cpr = ev.target.value.replace('-','')
          if (cpr.length === 10) {
              this.$route.query.case__cpr_number = cpr
              this.update()
          } else if (!cpr) {
              this.$route.query.case__cpr_number = ''
              this.update()
          }
      },
      changeWorker: function(worker_id) {
          if (this.$route.query.case__case_worker != worker_id) { // Only update if choice is different
              this.$route.query.case__case_worker = worker_id
              this.update()
          }
      },
      changeTeam: function(team_id) {
          if (this.$route.query.case__team != team_id) { // Only update if choice is different
              this.$route.query.case__team = team_id
              this.update()
          }
      }
  }

}