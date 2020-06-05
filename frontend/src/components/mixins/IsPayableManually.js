/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

 export default {
  computed: {
    results: function() {
      let payments = this.$store.getters.getPayments
      return payments.results
    },
    isPayableManually: function() {
      let payId = this.results.filter(pay => pay.id === this.rowId)
      if (payId) {
        for (let p in payId) {
          return payId[p].activity__status === 'GRANTED' && payId[p].is_payable_manually
        }
      }
    }
  }
}