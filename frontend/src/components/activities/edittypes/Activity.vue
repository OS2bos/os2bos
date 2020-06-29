<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <fieldset v-if="editable">
        <label class="required" for="fieldSelectAct">Ydelse</label>
        <p v-if="preselectedAct"><strong>{{ act_details[0].name }}</strong></p>
        <list-picker
            v-if="!preselectedAct && act_details"
            :dom-id="'fieldSelectAct'"
            :disabled="disableAct"
            :selected-id="model"
            @selection="changeActivityType"
            :list="act_details"
            required />
               
        <error :err-key="this.property" />

        <p v-if="model" style="margin-top: .5rem;">{{ act2description(model) }}</p>

    </fieldset>

    <dl v-else>
        <template v-if="model">
            <dt>Ydelse</dt>
            <dd>
                <p><strong v-html="act2name(model)"></strong></p>
                <p>{{ act2description(model) }}</p>
            </dd>
        </template>
    </dl>


</template>

<script>
import axios from '../../http/Http.js'
import mixin from '../../mixins/ActivityEditMixin.js'
import Error from '../../forms/Error.vue'
import ListPicker from '../../forms/ListPicker.vue'
import { activityId2name, activityId2description } from '../../filters/Labels.js'

export default {
    components: {
        Error,
        ListPicker
    },
    mixins: [
        mixin
    ],
    data: function() {
        return {
            act_details: null
        }
    },
    computed: {
        act: function() {
            return this.$store.getters.getActivity
        },
        appropriation: function() {
            return this.$store.getters.getAppropriation
        },
        appr_main_acts: function() {
            return this.$store.getters.getAppropriationMainActs
        },
        disableAct: function () {
            if (this.act_details && this.act_details.length < 1) {
                return true
            }
        },
        preselectedAct: function() {
            if (this.act_details && this.act_details.length === 1) {
                this.model = this.act_details[0].id
                return true
            } else {
                return false
            }
        }
    },
    methods: {
        changeActivityType: function(act_detail_id) {
            this.model = act_detail_id
            if (act_detail_id) {
                this.$store.dispatch('fetchActivityDetail', act_detail_id)
            }
        },
        act2name: function(id) {
            return activityId2name(id)
        },
        act2description: function(id) {
            return activityId2description(id)
        },
        generateActivityList: function() {
            if (this.editable) {
                let actList
                if (this.act.activity_type === 'MAIN_ACTIVITY') {
                    actList = `main_activity_for=${ this.appropriation.section }`
                } else {
                    actList = `supplementary_activity_for=${ this.appropriation.section }`
                    if (this.appr_main_acts) {
                        actList += `&main_activities=${ this.appr_main_acts.activities[0].details }`
                    }
                }
                axios.get(`/activity_details/?${ actList }`)
                .then(res => {
                    this.act_details = res.data
                })
                .catch(err => console.log(err))
            }
        }
    },
    created: function() {
        this.property = 'details'
        this.generateActivityList()
    }
}
</script>