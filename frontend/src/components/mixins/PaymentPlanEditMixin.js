/* Copyright (C) 2020 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

export default {

    props: {
        editable: {
            type: Boolean,
            default: false
        }
    },
    data: function() {
        return {
            property: null
        }
    },
    computed: {
        model: {
            get: function() {
                return this.$store.getters.getPaymentPlanProperty(this.property)
            },
            set: function(new_val) {
                this.$store.commit('setPaymentPlanProperty', {
                    prop: this.property,
                    val: new_val
                })
            }
        }
    }

}