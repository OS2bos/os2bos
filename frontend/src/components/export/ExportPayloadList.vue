<!-- Copyright (C) 2022 Magenta ApS, http://magenta.dk.
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
                <li v-for="obj in dst_export_objects" :key="obj.id" class="dst-export-list-item">
                    <a class="dst-export-list-item-link" :href="`/api/admin/core/dstpayload/${ obj.id }/`" target="_blank">
                        <i class="material-icons">description</i>
                        <span>
                            {{ displayTargetLabel(obj.dst_type) }}<br>
                            {{ displayCutoffDates(obj.from_date, obj.to_date) }}
                        </span>
                    </a>
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
    computed: {
        dst_export_objects: function() {
            return this.$store.getters.getDSTexportObjects
        }
    },
    methods: {
        displayDate: function(date) {
            return json2js(date)
        },
        displayCutoffDates: function(from_date, to_date) {
            let from_date_str = json2jsDate(from_date)
            if (!from_date || from_date === '1970-01-01') {
                from_date_str = 'Alle op'
            }
            return `${from_date_str} til ${json2jsDate(to_date)}`
        },
        displayTargetLabel: function(str) {
            if (str === 'HANDICAP') {
                return 'Handicapkompenserende indsatser'
            } else {
                return 'Forebyggende foranstaltninger'
            }
        }
    },
    created: function() {
        this.$store.dispatch('fetchDSTexportedObjects')
    }
}
</script>

<style>
    li.dst-export-list-item {
        padding: 0;
    }
    .dst-export-list-item-link {
        border-bottom: none !important;
        display: flex;
        flex-flow: row nowrap;
        gap: .75rem;
        align-items: center;
        padding: .5rem 1rem .75rem;
    }
    .dst-export-list-item-link:hover,
    .dst-export-list-item-link:active {
        background-color: var(--grey1);
    }
    .dst-export-list-item-link:focus {
        background-color: var(--grey1);
    }
    .dst-export-list-item-link .material-icons {
        font-size: 2.5rem;
    }
</style>
