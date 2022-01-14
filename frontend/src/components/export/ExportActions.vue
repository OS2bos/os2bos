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
        <fieldset style="margin: 0;">
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
            <label for="export-date">
                Eksportér ændringer fra denne dato:
                <br>
                <span class="dim">(Udelad for at vælge alle)</span>
            </label>
            <input id="export-date" type="date" v-model="export_date">
        </fieldset>
        <fieldset style="margin-top: 1.5rem;">
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
            export_test: true,
            export_date: null
        }
    },
    computed: {
        export_url: function() {
            let target_str = 'appropriations/generate_dst_preventative_measures_file/'
            const date_str = this.export_date ? `from_date=${this.export_date}` : 'from_date=1970-01-01'
            if (this.export_target === 'TARGET2') {
                target_str = 'appropriations/generate_dst_handicap_file/'
            }
            if (!this.export_test) {     
                return `/${target_str}?test=false&${date_str}`
            } else {
                return `/api/${target_str}?test=true&${date_str}`
            }
            
        }
    },
    methods: {
        exportData: function(ev) {
            if (confirm('Er du sikker på, at du vil eksportere data til DST?')) {
                axios.get(this.export_url)
                .then(res => {
                    this.$store.dispatch('fetchDSTexportedObjects')
                    alert('Eksport er gennemført')
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
        min-width: 19rem;
        padding: 1rem 2rem;
        margin-top: 2rem;
    }
    .dst-export-actions fieldset {
        margin-bottom: .5rem;
    }
    .dst-export-actions .warning-icon {
        font-size: 1rem;
        margin-right: .5rem;
    }
</style>
