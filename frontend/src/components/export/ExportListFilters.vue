<!-- Copyright (C) 2022 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <form @submit.prevent class="dst-export-filters">
        <fieldset>
            <label for="field-section">Bevillinger efter §</label>
            <list-picker
                class="resize"
                :dom-id="'field-section'"
                :list="sections"
                @selection="filterBySection"
                display-key="paragraph"
                display-key2="text"
            />
        </fieldset>
        <fieldset style="display: flex; flex-flow: row nowrap; gap: .5rem;">
            <div>
                <label for="from-date">
                    Fra dato:
                </label>
                <input id="from-date" type="date" v-model="from_date" :max="to_date" @change="filterByCutoff"><br>
                <span class="dim" style="font-size: smaller;">(Udelad for at vælge alle)</span>
            </div>
            <div>
                <label for="to-date">Til dato:</label>
                <input id="to-date" type="date" v-model="to_date" :max="today" required @change="filterByCutoff">
            </div>
            <p style="padding-top: 2rem;">&hellip;eller&hellip;</p>
            <div>
                <label for="preview-mode">Hurtigt datovalg</label>
                <select id="preview-mode" class="listpicker" @change="quickSetDateFilter" v-model="quickset">
                    <option value="custom">---</option>
                    <option value="all">Alle ændringer</option>
                    <option :disabled="!latest_dst_export" value="newer">
                        Ændringer siden seneste eksport
                    </option>
                    <option :disabled="!latest_dst_export" value="older">
                        Ændringer før seneste eksport
                    </option>
                </select>
            </div>
        </fieldset>
    </form>

</template>

<script>
    import ListPicker from '../forms/ListPicker.vue'
    import {json2jsDate, epoch2DateStr} from '../filters/Date.js'

    export default {
        components: {
            ListPicker
        },
        props: [
            'sections'
        ],
        data: function () {
            return {
                from_date: null,
                to_date: epoch2DateStr(new Date()),
                today: epoch2DateStr(new Date()),
                quickset: 'custom',
                currentSection: null
            }
        },
        computed: {
            latest_dst_export: function() {
                return this.$store.getters.getLatestDSTexport
            }
        },
        methods: {
            displayLatestDate: function(date) {
                if (date && date !== '1970-01-01') {
                    return json2jsDate(date)
                } else {
                    return ''
                }
            },
            filterByCutoff: function() {
                this.quickset = 'custom'
                this.emitChange()
            },
            filterBySection: function(section_id) {
                if (section_id) {
                    this.currentSection = section_id
                    this.emitChange()
                }
            },
            emitChange: function() {
                this.$emit('change', {
                    section: this.currentSection,
                    to_date: this.to_date,
                    from_date: this.from_date
                })
            },
            quickSetDateFilter: function(event) {
                switch(event.target.value) {
                    case 'all':
                        this.to_date = this.today
                        this.from_date = null
                        break;
                    case 'older':
                        const day_before_last = epoch2DateStr(new Date().setDate(new Date(this.latest_dst_export.to_date).getDate() - 1 ))
                        this.to_date = day_before_last
                        this.from_date = null
                        break;
                    case 'newer':
                        this.to_date = this.today
                        this.from_date = this.latest_dst_export.to_date
                        break;
                    default:
                        // 'custom'
                }
                this.emitChange()
            }
        }
    }
    
</script>

<style>
    .dst-export-filters {
        padding: .5rem 2rem .5rem 0;
        display: flex;
        flex-flow: row wrap;
    }
    .dst-export-filters fieldset {
        margin: 0 0 .5rem 2rem;
    }
</style>