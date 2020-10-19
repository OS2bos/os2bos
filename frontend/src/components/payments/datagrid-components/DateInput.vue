<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    
    <div v-if="visible">
        <popover :condition="display_warning">{{ display_warning }}</popover>
        <input :ref="`dateInput${ rowid }`" v-if="visible" type="date" v-model="date">
    </div>
    <span v-else class="date-paid">
        {{ displayPayDate(date) }}
    </span>
</template>

<script>

import PermissionLogic from '../../mixins/PermissionLogic.js'
import { json2jsDate } from '../../filters/Date.js'
import Popover from '../../warnings/Popover.vue'

export default {
    mixins: [ 
        PermissionLogic
    ],
    props: [
        'rowid',
        'compdata'
    ],
    components: {
        Popover
    },
    data: function() {
        return {
            display_warning: null
        }
    },
    computed: {
        date: {
            get: function() {
                return this.compdata.paid_date
            },
            set: function(new_val) {
                this.$store.commit('setPaymentEditRowData', {
                    idx: this.rowid,
                    prop: 'paid_date',
                    val: new_val
                })
            }
        },
        visible: function() {
            return this.is_payable(this.compdata)
        }
    },
    methods: {
        displayPayDate: function(payment) {
            return json2jsDate(payment)
        },
        focusHandler: function() {
            this.display_warning = this.warn_edit_payment(this.compdata)
        },
        blurHandler: function() {
            this.display_warning = null
        }
    },
    mounted: function() {
        let input_id = `dateInput${ this.rowid }`
        if (this.$refs[input_id]) {
            this.$refs[input_id].addEventListener('focus', this.focusHandler)
            this.$refs[input_id].addEventListener('blur', this.blurHandler)
        }
    }
}
</script>