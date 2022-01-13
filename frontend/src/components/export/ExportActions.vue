<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <form class="dst-export-actions" @submit.prevent="exportData">
        <h2>Eksporter data</h2>
        <fieldset>

            <warning v-if="!export_test" content="Dette udtræk vil blive leveret til DST" />

            <input 
                type="checkbox" 
                name="export-test" 
                v-model="export_test" 
                id="export-test-checkbox">
            <label for="export-test-checkbox">Testudtræk (sendes ikke til DST)</label>
        </fieldset>
        <fieldset>
            <input 
                type="radio" 
                value="TARGET1" 
                v-model="export_target" 
                id="export-target-radio-1">
            <label for="export-target-radio-1">Familieområdet</label>

            <input 
                type="radio" 
                value="TARGET2"
                v-model="export_target" 
                id="export-target-radio-2">
            <label for="export-target-radio-2">Handicapområdet</label>
        </fieldset>
        <fieldset>
            <a v-if="export_test" :href="export_url" target="_blank">
                <i class="material-icons">file_download</i>
                Hent testudtræk
            </a>
            <button v-if="!export_test" type="submit">Eksporter</button>
        </fieldset>
    </form>
    
</template>

<script>
import axios from '../http/Http.js'
import Warning from '../warnings/Warning.vue'

export default {
    components: {
        Warning
    },
    data: function () {
        return {
            export_target: "TARGET1",
            export_test: true
        }
    },
    computed: {
        export_url: function() {
            let target_str = 'appropriations/generate_dst_preventative_measures_file/'
            if (this.export_target === 'TARGET2') {
                target_str = 'appropriations/generate_dst_handicap_file/'
            }
            if (!this.export_test) {     
                return `/${target_str}?test=false&from_start_date=1970-01-01`
            } else {
                return `/api/${target_str}?test=true&from_start_date=1970-01-01`
            }
            
        }
    },
    methods: {
        exportData: function(ev) {
            if (confirm('Er du sikker på, at du vil eksportere data til DST?')) {
                axios.get(this.export_url)
                .then(res => {
                    this.$store.dispatch('fetchDSTexportedObjects')
                    alert('det lykkedes at eksportere noget')
                })
                .catch(err => {
                    console.error(err)
                })
            }
        }
    },
    created: function() {
        
    }
}
</script>

<style>
    .dst-export-actions {
        min-width: 17rem;
    }
    .dst-export-actions .warning-icon {
        font-size: 1rem;
        margin-right: .5rem;
    }
</style>
