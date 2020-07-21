<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <fieldset v-if="editable">
        <input type="checkbox" v-model="status" id="status">
        <label for="status">Forventet ydelse</label>
    </fieldset>

    <dl v-else>
        <dt>Status</dt>
        <dd v-html="statusLabel(model)"></dd>
    </dl>
</template>

<script>
import mixin from '../../mixins/ActivityEditMixin.js'
import { displayStatus } from '../../filters/Labels.js'

export default {
    
    mixins: [
        mixin
    ],
    computed: {
        status: {
            get: function() {
                return this.model === 'EXPECTED' ? true : false 
            }, 
            set: function(new_val) {
                if (this.editable) {
                    if (new_val) {
                        this.model = 'EXPECTED'
                    } else {
                        this.model = 'DRAFT'
                    }
                }   
            }
        }
    },
    created: function() {
        this.property = 'status'
    }
}
</script>