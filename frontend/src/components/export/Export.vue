<!-- Copyright (C) 2022 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <article class="dst-export">

        <header class="case-search-header">
            <h1>Dataudtræk til DST</h1>
        </header>

        <div class="dst-export-content">
        
            <section class="dst-export-items">
                <form @submit.prevent>
                    <fieldset class="filter-fields">
                        <div class="filter-field">
                            <label for="preview-mode">Visning</label>
                            <select id="preview-mode" class="listpicker" @change="filterByCutoff" v-model="currentPreviewMode">
                                <option value="all">Alle ændringer</option>
                                <option :disabled="!latest_dst_export_date" value="newer">Ændringer siden seneste eksport {{ displayLatestDate(latest_dst_export_date) }}</option>
                                <option disabled value="older">Ændringer før seneste eksport</option>
                            </select>
                        </div>
                        <div class="filter-field">
                            <label for="field-section">Bevillinger efter §</label>
                            <list-picker
                                class="resize"
                                :dom-id="'field-section'"
                                :list="sectionlist"
                                @selection="filterBySection"
                                display-key="paragraph"
                                display-key2="text"
                            />
                        </div>
                    </fieldset>
                </form>
                <data-grid
                    ref="data-grid"
                    :data-list="appropriationlist"
                    :columns="columns"
                    :selectable="false">

                    <p slot="datagrid-header">
                        <span v-html="currentSectionDisplay"></span><br>
                        <span v-html="numberOfCPRsDisplay"></span>
                    </p>

                </data-grid>
            </section>

            <section class="dst-export-xml">
                <export-actions />
                <export-payload-list />
            </section>

        </div>
            
    </article>

</template>

<script>
    import ListPicker from '../forms/ListPicker.vue'
    import DataGrid from '../datagrid/DataGrid.vue'
    import axios from '../http/Http.js'
    import ExportPayloadList from './ExportPayloadList.vue'
    import ExportActions from './ExportActions.vue'
    import {json2jsDate} from '../filters/Date.js'

    export default {
        components: {
            ListPicker,
            DataGrid,
            ExportPayloadList,
            ExportActions
        },
        data: function () {
            return {
                now: Date.now(),
                sectionlist: [],
                appropriationlist: [],
                currentSection: null,
                currentPreviewMode: this.latest_dst_export_date ? 'newer' : 'all',
                columns: [
                    {
                        key: 'case_cpr',
                        title: 'CPR'
                    },
                    {
                        key: 'sbsysId',
                        title: 'Bevilling',
                        display_func: function(d) {
                            let to = `#/appropriation/${ d.pk }/`
                            return `
                                <a href="${ to }">
                                    <i class="material-icons">folder_open</i>
                                    ${ d.sbsysId }
                                </a>
                            `
                        },
                        class: 'datagrid-action nowrap'
                    },
                    {
                        key: 'main_activity_name',
                        title: 'Hovedydelse',
                        display_func: function(d) {
                            let to = `#/activity/${ d.main_activity_pk }/`
                            return `<a href="${ to }"><i class="material-icons">style</i> ${ d.main_activity_name }</a>`
                        },
                        class: 'datagrid-action nowrap'
                    },
                    {
                        key: 'main_activity_startdate',
                        display_func: function(d) {
                            return json2jsDate(d.main_activity_startdate)
                        },
                        title: 'Startdato'
                    },
                    {
                        key: 'main_activity_enddate',
                        display_func: function(d) {
                            return json2jsDate(d.main_activity_enddate)
                        },
                        title: 'Slutdato'
                    },
                    {
                        key: 'dst_report_type',
                        title: 'Ny/Ændret',
                        display_func: function(d) {
                            return `<span class="datagrid-${ d.dst_report_type }">${ d.dst_report_type ? d.dst_report_type : 'Uændret' }</span>`
                        }
                    }
                ]
            }
        },
        computed: {
            latest_dst_export_date: function() {
                return this.$store.getters.getLatestDSTexportDate
            },
            currentSectionDisplay: function() {
                const section = this.sectionlist.filter(s => {
                    return this.currentSection === s.id
                })
                if (section.length < 1) {
                    return 'Fandt ingen ydelser for denne paragraf'
                } else {
                    return `Viser <strong>${this.appropriationlist.length}</strong> poster for §${section[0].paragraph} ${section[0].text} (DST-kode: ${section[0].dstCode})`
                }
            },
            numberOfCPRsDisplay: function() {
                if (this.appropriationlist.length < 1) {
                    return ''
                }
                const cprs = this.appropriationlist.map(e => {
                    return e.case_cpr
                })
                return `Fordelt på <strong>${ [...new Set(cprs)].length }</strong> CPR-numre`
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
            buildFilterString: function(preview_mode, section_id) {
                let filter = `section:"${section_id}"`
                if (preview_mode === 'newer') {
                    filter += `, fromDstStartDate:"${this.latest_dst_export_date}"`
                }
                return filter
            },
            filterByCutoff: function(event) {
                this.currentPreviewMode = event.target.value
                this.fetchAppropriations(this.buildFilterString(event.target.value, this.currentSection))
                .then(res => {
                    this.appropriationlist = this.sanitizeAppropriationData(res)
                })
                .catch(err => {
                    console.error(err)
                })
            },
            filterBySection: function(section_id) {
                if (section_id) {
                    this.currentSection = section_id
                    this.fetchAppropriations(this.buildFilterString(this.currentPreviewMode, section_id))
                    .then(res => {
                        this.appropriationlist = this.sanitizeAppropriationData(res)
                    })
                    .catch(err => {
                        console.error(err)
                    })
                }
            },
            fetchSections: function(sections, pageInfo) {
                const filterstr = pageInfo && pageInfo.hasNextPage ? `(after: "${pageInfo.endCursor}")` : ''
                return axios.post('/graphql/', { query: `
                    {
                        sections${filterstr} {
                            pageInfo {
                                endCursor,
                                hasNextPage
                            },
                            edges {
                                node {
                                    id,
                                    paragraph,
                                    text,
                                    pk,
                                    dstCode,
                                    dstPreventativeMeasures,
                                    dstHandicap
                                }
                            }
                        }
                    }
                ` })
                .then(res => {
                    const mypageinfo = res.data.data.sections.pageInfo
                    const mysections = res.data.data.sections.edges.filter(e => {
                        if (e.node.dstPreventativeMeasures || e.node.dstHandicap) {
                            return e
                        }
                    })
                    .map(n => {
                        return n.node
                    })
                    
                    const newsectionlist = sections.concat(mysections)
                    if (mypageinfo.hasNextPage) {
                        return this.fetchSections(newsectionlist, mypageinfo)
                    } else {
                        return newsectionlist
                    }   
                })
            },
            fetchAppropriations: function(filters) {
                return axios.post('/graphql/', { query: `
                    {
                        appropriations(${filters}) {
                            edges {
                                node {
                                    pk,
                                    sbsysId,
                                    dstReportType,
                                    case {
                                        cprNumber
                                    },
                                    mainActivities: activities(activityType: "MAIN_ACTIVITY", status: "GRANTED") {
                                        edges {
                                            node {
                                                pk,
                                                startDate,
                                                endDate,
                                                details {
                                                    name
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                ` })
                .then(res => {
                    if (res.data.data.appropriations) {
                        return res.data.data.appropriations.edges.map(e => e.node)
                    }
                })
            },
            sanitizeAppropriationData: function(data) {
                let appropriationdata = data.filter(apprs => {
                    return apprs.mainActivities.edges.length > 0
                })
                .map(d => {
                    const activity_meta = this.sanitizeActivityData(d.mainActivities.edges)
                    return {
                        pk: d.pk,
                        sbsysId: d.sbsysId,
                        case_cpr: d.case.cprNumber,
                        main_activity_pk: activity_meta.pk,
                        main_activity_name: activity_meta.name,
                        main_activity_startdate: activity_meta.startDate,
                        main_activity_enddate: activity_meta.endDate,
                        dst_report_type: d.dstReportType
                    }
                })
                return appropriationdata
            },
            sanitizeActivityData: function(data) {
                if (data.length < 1) {
                    return false
                }

                // We're using spread operator to clone the 'data' Array 
                // to make sure the sorted arrays don't overwrite each other
                let sorted_by_start = [...data].sort(function(a,b) {
                    return a.node.startDate >= b.node.startDate
                })
                let sorted_by_end = [...data].sort(function(a,b) {
                    if (!a.node.endDate || !b.node.endDate) {
                        return true
                    } else {
                        return a.node.endDate <= b.node.endDate
                    }
                })
                return {
                    pk: sorted_by_start[0].node.pk,
                    name: sorted_by_start[0].node.details.name,
                    startDate: sorted_by_start[0].node.startDate,
                    endDate: sorted_by_end[0].node.endDate,
                }
            }
        },
        created: function() {

            // Fetch a list of sections for the filter dropdown
            this.fetchSections([], false)
            .then(res => {
                this.sectionlist = res
            })
        }
    }
    
</script>

<style>
    .dst-export {
        padding: 0 2rem 2rem;
        max-width: 100%;
    }
    .dst-export .filter-fields {
        display: flex;
        flex-flow: row nowrap;
    }
    .dst-export .filter-field {
        margin-right: 1rem;
    }
    .dst-export-content {
        display: flex;
        flex-flow: row;
    }
    .dst-export-items {
        flex-grow: 1;
        border-right: 1px solid var(--grey1);
        padding-right: 2rem;
        margin-right: 2rem;
    }

    .datagrid-Ny::before,
    .datagrid-Ændring::before {
        content: '';
        margin-right: .5rem;
        border-radius: 50%;
        width: 1rem;
        height: 1rem;
        overflow: hidden;
        display: inline-block;
        vertical-align: middle;
    }
    .datagrid-Ny::before { 
        background-color: var(--success);
    }
    .datagrid-Ændring::before {
        background-color: var(--warning);
    }
    
</style>