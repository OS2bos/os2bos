<!-- Copyright (C) 2022 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <form class="dst-export-actions" @submit.prevent="exportData">
        <h2>Eksporter data</h2>
        <fieldset>

            <warning v-if="!export_test" content="Dette udtræk vil blive registreret som en eksport til DST" />

            <input 
                type="checkbox" 
                name="export-test" 
                v-model="export_test" 
                id="export-test-checkbox">
            <label for="export-test-checkbox">Testudtræk (registreres ikke)</label>
        </fieldset>
        <fieldset style="margin: 0;">
            <input
                type="radio" 
                value="TARGET1" 
                v-model="export_target" 
                id="export-target-radio-1">
            <label for="export-target-radio-1">Forebyggende foranstaltninger</label>

            <input
                type="radio" 
                value="TARGET2"
                v-model="export_target" 
                id="export-target-radio-2">
            <label for="export-target-radio-2">Handicapkompenserende indsatser</label>
        </fieldset>
        <fieldset style="display: flex; flex-flow: row nowrap; gap: .5rem;">
            <div>
                <label for="export-from-date">
                    Fra dato:
                </label>
                <input id="export-from-date" type="date" v-model="export_from_date" :max="today"><br>
                <span class="dim" style="font-size: smaller;">(Udelad for at vælge alle)</span>
            </div>
            <div>
                <label for="export-to-date">Til dato:</label>
                <input id="export-to-date" type="date" v-model="export_to_date" :max="today" required>
            </div>
        </fieldset>
        <fieldset>
            <a v-if="export_test" :href="`/api${export_url}`" target="_blank" class="btn dst-export-test-link">
                <i class="material-icons">file_download</i>
                Hent testudtræk
            </a>
            <button v-else type="submit" class="dst-export-button">
                <i class="material-icons">file_download</i>
                Eksportér
            </button>
        </fieldset>
    </form>
    
</template>

<script>
import Warning from '../warnings/Warning.vue'
import {epoch2DateStr} from '../filters/Date.js'

export default {
    components: {
        Warning
    },
    data: function () {
        return {
            export_target: "TARGET1",
            export_test: true,
            export_from_date: null,
            export_to_date: epoch2DateStr(new Date()),
            today: epoch2DateStr(new Date())
        }
    },
    computed: {
        export_url: function() {
            let target_str = 'appropriations/generate_dst_preventative_measures_file/'
            if (this.export_target === 'TARGET2') {
                target_str = 'appropriations/generate_dst_handicap_file/'
            }

            let date_str = ''
            if (this.export_to_date) {
                date_str += `&to_date=${this.export_to_date}`
            }
            if (this.export_from_date) {
                date_str += `&from_date=${this.export_from_date}`
            }
            
            let test_str = 'test=true'
            if (!this.export_test) {
                test_str = 'test=false'
            }

            return `/${target_str}?${test_str}${date_str}`
        }
    },
    methods: {
        exportData: function(event) {
            if (confirm('Er du sikker på, at du vil eksportere data?')) {
                window.open(`/api${this.export_url}`, '_blank')
                setTimeout(() => {
                    this.$store.dispatch('fetchDSTexportedObjects')
                }, 500)
            }
        }
    }
}
</script>

<style>
    .dst-export-actions {
        min-width: 19rem;
        padding: 1rem 2rem;
        margin-bottom: 2rem;
    }
    .dst-export-actions fieldset {
        margin-bottom: .5rem;
    }
    .dst-export-actions .warning-icon {
        font-size: 1rem;
        margin-right: .5rem;
    }

    .dst-export-test-link,
    .dst-export-button {
        display: flex !important;
        flex-flow: row nowrap;
        align-items: center;
        margin-top: 1rem;
    }
    .dst-export-test-link {
        width: 10rem !important;
    }
</style>
