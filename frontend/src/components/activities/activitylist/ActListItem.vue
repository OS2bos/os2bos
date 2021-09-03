<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <div v-if="is_visible" 
        class="act-list-row" 
        :class="{'act-list-sub-row': isGroup}"
        :data-row-id="activity.id">
        <div style="padding: .5rem 0 0 1.25rem;">
            <template v-if="activity.status !== 'GRANTED'">
                <input 
                    v-if="user_can_edit === true && this.user.profile !== 'edit'" 
                    type="checkbox" 
                    :id="`check-${ activity.id }`" 
                    v-model="is_checked">
                <label 
                    class="disabled" 
                    :for="`check-${ activity.id }`" 
                    title="Udvælg denne ydelse">
                </label>
            </template>
        </div>
        <div>
            <div class="mini-label" v-html="statusLabel(activity.status)"></div>
        </div>
        <div :title="activity.details.name" class="data-grid-action nowrap">
            <router-link :to="`/activity/${ activity.id }/`">{{ activity.details.name }}</router-link>
            <br>
            <span class="dim" v-if="activity.payment_plan && activity.payment_plan.fictive">(Fiktiv)</span>
        </div>
        <div class="nowrap" :title="activity.note">
            <span v-if="activity.note">{{ activity.note }}</span>
            <span v-else>-</span>
        </div>
        <div>
            <div v-if="activity.payment_plan" :title="activity.payment_plan.recipient_name">
                {{ activity.payment_plan.recipient_name }}
                <span v-if="activity.payment_plan.recipient_type === 'COMPANY'">
                    CVR
                </span>
                {{ activity.payment_plan.recipient_id }}
            </div>
        </div>
        <div class="nowrap">{{ displayDate(activity.start_date) }}</div>
        <div class="nowrap">{{ displayDate(activity.end_date) }}</div>
        <div class="nowrap">{{ displayDate(activity.modified) }}</div>
        <div class="nowrap right" :title="displayCost(activity, 'granted')">
            {{ displayCost(activity, 'granted') }}
        </div>
        <div class="nowrap right" :title="displayCost(activity, 'expected')">
            <span :class="activity.status === 'DRAFT' ? 'dim' : 'expected'">
                {{ displayCost(activity, 'expected') }}
            </span>
        </div>
    </div>
</template>

<script>
import ActListMixin from './ActListMixin.js'
import PermissionLogic from '../../mixins/PermissionLogic.js'

export default {
    mixins: [
        ActListMixin,
        PermissionLogic
    ],
    props: [
        'activity',
        'displayOld',
        'isGroup'
    ],
    computed: {
        is_visible: function() {
            if (!this.displayOld && this.activity.is_old) {
                return false
            } else {
                return true
            }
        },
        is_checked: {
            get: function() {
                return this.$store.getters.checkItem(this.activity)
            },
            set: function(new_val) {
                if (new_val) {
                    this.$store.commit('setCheckedItem', this.activity)
                } else {
                    this.$store.commit('removeCheckedItem', this.activity)
                }
            }
        }
    }
}
</script>

<style>

    .act-list-row.act-list-sub-row {
        background-color: hsl(var(--color1), 66%, 92%);
    }

    .act-list-row .data-grid-action > a {
        display: inline-block;
        text-decoration: none;
        border: none;
        transition: transform .33s;
    }

    .act-list-row .data-grid-action > a:hover, 
    .act-list-row .data-grid-action > a:active,
    .act-list-row .data-grid-action > a:focus {
        transform: translate(.75rem, 0);
    }

</style>