<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <div>
        <activity-list-meta-item 
            v-if="activities.length > 1"
            :meta-activity="meta_activity"
            @toggle="toggleHandler" />
        <template v-if="expanded || activities.length === 1">
            <activity-list-item 
                v-for="act in activities" 
                :key="act.id" 
                :activity="act"
                :display-old="displayOld"
                :is-group="activities.length > 1"
                :class="{'act-list-sub-row': activities.length > 1}" />
        </template>
    </div>
</template>

<script>
import ActivityListMetaItem from './ActListMetaItem.vue'
import ActivityListItem from './ActListItem.vue'

export default {
    components: {
        ActivityListMetaItem,
        ActivityListItem
    },
    props: [
        'activities',
        'displayOld'
    ],
    data: function() {
        return {
            expanded: false
        }
    },
    computed: {
        meta_activity: function() {
            const acts = this.activities,
                last_act = acts[acts.length - 1],
                costs = this.calcCost(acts)

            return {
                status: this.checkExpected(acts),
                start_date: this.getBestDate(acts, 'start'),
                end_date: this.getBestDate(acts, 'end'),
                modified: this.getBestModified(acts),
                activity_type: last_act.activity_type,
                approved: costs.approved,
                expected: costs.expected,
                details: last_act.details,
                payment_plan: last_act.payment_plan,
                note: last_act.note
            }
        }
    },
    watch: {
        displayOld: function(new_val, old_val) {
            if (new_val && !this.expanded) {
                this.expanded = true
            }
        }
    },
    methods: {
        toggleHandler: function(payload) {
            this.expanded = payload.toggled
        },
        getBestDate(arr, criteria) {
            let best_date = null
            if (criteria === 'start') {
                best_date = arr[0].start_date
            } else {
                best_date = arr[arr.length - 1].end_date
            }
            return best_date
        },
        checkExpected(arr) {
            return arr.find(function(a) {
                return a.status === 'EXPECTED'
            }) ? 'EXPECTED' : arr[0].status
        },
        calcCost(arr) {
            let costs = {
                approved: 0,
                expected: 0
            }
            for (let a of arr) {
                if (a.total_granted_this_year) {
                    costs.approved = costs.approved + a.total_granted_this_year
                }
                if (a.total_expected_this_year) {
                    costs.expected = costs.expected + a.total_expected_this_year
                }
            }
            return costs
        },
        getBestModified(arr) {
            return arr[arr.length - 1].modified
        }
    }
}
</script>