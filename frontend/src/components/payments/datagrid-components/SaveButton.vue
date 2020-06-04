<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <button type="button" :disabled="disabled" @click="submitHandler">Gem</button>
</template>

<script>
export default {
    props: {
        rowId: Number
    },
    data: function() {
        return {
            date_el: null,
            amount_el: null
        }
    },
    computed: {
        disabled: function() {
            if (this.date_el && this.amount_el) {
                console.log(this.date_el.value, this.amount_el.value)
                if (this.date_el.value === "" || !this.amount_el.value) {
                    return true
                } else {
                    return false
                }
            }
        }
    },
    methods: {
        submitHandler: function() {
            
            console.log(this.date_el.value, this.amount_el.value)

        }
    },
    mounted: function() {
        this.date_el = document.getElementById(`field-date-${ this.rowId }`)
        this.amount_el = document.getElementById(`field-amount-${ this.rowId }`)
    }
}
</script>