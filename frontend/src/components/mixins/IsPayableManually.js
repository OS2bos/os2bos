/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

 export default {
  computed: {
    payments: function() {
      let payments = this.$store.getters.getPayments
      return payments.results
    },
    isPayableManually: function() {
      let pay = this.payments.filter(pay => pay.id === this.rowId)
      for (let p in pay) {
          return pay[p].activity__status === 'GRANTED' && pay[p].is_payable_manually && pay[p].paid === false
      }
    }
  }
}