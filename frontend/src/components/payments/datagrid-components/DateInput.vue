<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    
    <div v-if="visible">
        <popover :condition="display_warning">{{ display_warning }}</popover>
        <input type="date" v-model="paydate" @focus="focusHandler" @blur="blurHandler">
    </div>
    <span v-else class="date-paid">
        {{ display_pay_date }}
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
            paydate: this.compdata.paid_date,
            display_warning: null
        }
    },
    computed: {
        visible: function() {
            return this.is_payable(this.compdata)
        },
        display_pay_date: function() {
            return json2jsDate(this.paydate)
        }
    },
    watch: {
        compdata: function(new_val, old_val) {
            if (new_val !== old_val) {
                this.paydate = new_val.paid_date
            }
        },
        paydate: function(new_val) {
            let new_data = Object.assign({}, this.compdata)
            new_data.paid_date = new_val
            this.$emit('update', {operation: 'update', data: new_data})
        }
    },
    methods: {
        focusHandler: function() {
            this.display_warning = this.warn_edit_payment({
                payment_method: this.compdata.payment_method,
                date: this.compdata.date
            })
        },
        blurHandler: function() {
            this.display_warning = null
        }
    }
}
</script>