<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    
    <div @click="toggle" class="act-list-row act-list-meta-row">
        <div style="padding: .5rem 0 0 1.25rem;">
            <i class="material-icons dropdown-arrow" :class="{'toggled': toggled}">expand_more</i>
        </div>
        <div>
            <div class="mini-label" v-html="statusLabel(metaActivity.status)"></div>
        </div>
        <div :title="activityId2name(metaActivity.details)">
            <span v-html="activityId2name(metaActivity.details)"></span>
            <span class="dim" v-if="metaActivity.payment_plan.fictive">(Fiktiv)</span>
        </div>
        <div class="nowrap" :title="metaActivity.note">
            <span v-if="metaActivity.note">{{ metaActivity.note }}</span>
            <span v-else>-</span>
        </div>
        <div>
            <div v-if="metaActivity.payment_plan" :title="metaActivity.payment_plan.recipient_name">
                {{ metaActivity.payment_plan.recipient_name }}
                <span v-if="metaActivity.payment_plan.recipient_type === 'COMPANY'">
                    CVR
                </span>
                {{ metaActivity.payment_plan.recipient_id }}
            </div>
        </div>
        <div class="nowrap">{{ displayDate(metaActivity.start_date) }}</div>
        <div class="nowrap">{{ displayDate(metaActivity.end_date) }}</div>
        <div class="nowrap">{{ displayDate(metaActivity.modified) }}</div>
        <div class="nowrap right" :title="displayCost(metaActivity, 'granted', true)">
            {{ displayCost(metaActivity, 'granted', true) }}
        </div>
        <div class="nowrap right" :title="displayCost(metaActivity, 'expected', true)">
            <span :class="metaActivity.status === 'DRAFT' ? 'dim' : 'expected'">
                {{ displayCost(metaActivity, 'expected', true) }}
            </span>
        </div>
    </div>
    
</template>

<script>
import ActListMixin from './ActListMixin.js'
import PermissionLogic from '../../mixins/PermissionLogic.js'
import ActivityListItem from './ActListItem.vue'

export default {
    mixins: [
        ActListMixin,
        PermissionLogic
    ],
    props: [
        'metaActivity'
    ],
    data: function() {
        return {
            toggled: false
        }
    },
    methods: {
        toggle: function() {
            this.toggled = !this.toggled
            this.$emit('toggle', {toggled: this.toggled})
        }
    }
}
</script>

<style>
    .act-list-meta-row {
        cursor: pointer;
    }

    .act-list-meta-row .dropdown-arrow {
        transition: transform .25s;
    }

    .act-list-meta-row .dropdown-arrow.toggled {
        transform: rotate(-180deg);
    }

</style>