<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <article class="dst-export-list">
        <h2>DST eksporter</h2>
        <template v-if="dst_export_objects.length > 0">
            <ul class="list">
                <li v-for="obj in dst_export_objects" :key="obj.id">
                    <a class="dst-export-list-item-link" :href="`/api/admin/core/dstpayload/${ obj.id }/`" target="_blank">
                        <span>{{ displayTargetLabel(obj.dst_type) }}</span>
                        <span>{{ displayDate(obj.date) }}</span>
                    </a>
                    <br>
                    {{ displayCutoffDate(obj.from_date) }}
                    <br>
                </li>
            </ul>
        </template>
        <template v-else>
            Ingen data er eksporteret endnu.
        </template>
    </article>
    
</template>

<script>
import {json2js, json2jsDate} from '../filters/Date.js'

export default {
    data: function () {
        return {
            wait_time: 5*60*1000// 5 mins in millisecs
        }
    },
    computed: {
        dst_export_objects: function() {
            return this.$store.getters.getDSTexportObjects
        },
        latest_dst_export_date: function() {
            return this.$store.getters.getLatestDSTexportDate
        }
    },
    methods: {
        displayDate: function(date) {
            return json2js(date)
        },
        displayCutoffDate: function(date) {
            return json2jsDate(date)
        },
        displayTargetLabel: function(str) {
            if (str === 'HANDICAP') {
                return 'Handicapområdet'
            } else {
                return 'Familieområdet'
            }
        }
    },
    created: function() {
        this.$store.dispatch('fetchDSTexportedObjects')
    }
}
</script>

<style>
    .dst-export-list-item-link {
        display: flex;
        flex-flow: row nowrap;
        justify-content: space-between;
    }
</style>
