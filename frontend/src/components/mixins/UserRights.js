/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

export default {
  computed: {
    user: function() {
      return this.$store.getters.getUser
    },
    permissionCheck () {
      if (this.user.profile === 'admin') {
        return true
      }
      if (this.user.profile === 'workflow_engine') {
        return true
      }
      if (this.user.profile === 'grant') {
        return true
      }
      if (this.user.profile === 'edit') {
        return true
      }
      if (this.user.profile === 'readonly') {
        return false
      }
    }
  },
  watch: {
    user: function(new_val) {
      if (new_val) {
        this.$store.dispatch('fetchTeam', new_val.team)
      }
      this.update()
    }
  }
}