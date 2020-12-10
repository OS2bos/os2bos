/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

export default {
  // Debounce helper method lets a function await execution until it is no longer called again.
  // Useful for waiting for a user to stop typing in an input field.
  methods: {
    debounce: function(func, wait) {
      let timeout
      return function() {
            let context = this, 
                args = arguments
        const later = function() {
          timeout = null
          func.apply(context, args)
        }
        clearTimeout(timeout)
        timeout = setTimeout(later, wait)
      }
    }
  }
}
