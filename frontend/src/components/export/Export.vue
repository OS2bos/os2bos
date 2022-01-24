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
                <export-filters :sections="sectionlist" @change="updateAppropriations" />

                <p style="margin: 1rem 0 .5rem;">
                    <span v-html="measureClassDisplay" style="float: right;"></span>
                    <span v-html="currentSectionDisplay"></span><br>
                    <span v-html="numberOfCPRsDisplay"></span>
                </p>

                <export-list :appropriations="appropriationlist" />
            </section>

            <section class="dst-export-xml">
                <export-actions />
                <export-payload-list />
            </section>

        </div>
            
    </article>

</template>

<script>
    import axios from '../http/Http.js'
    import ExportFilters from './ExportListFilters.vue'
    import ExportList from './ExportList.vue'
    import ExportPayloadList from './ExportPayloadList.vue'
    import ExportActions from './ExportActions.vue'

    export default {
        components: {
            ExportPayloadList,
            ExportActions,
            ExportList,
            ExportFilters
        },
        data: function () {
            return {
                sectionlist: [],
                appropriationlist: [],
                currentSectionId: null
            }
        },
        computed: {
            currentSection: function() {
                if (this.currentSectionId && this.sectionlist.length > 0) {
                    return this.sectionlist.find(s => {
                        return this.currentSectionId === s.id
                    })
                } else {
                    return false
                }
            },
            currentSectionDisplay: function() {
                if (!this.currentSection) {
                    return 'Fandt ingen ydelser for denne paragraf'
                } else {
                    return `Viser <strong>${this.appropriationlist.length}</strong> poster for §${this.currentSection.paragraph} ${this.currentSection.text} (DST-kode: ${this.currentSection.dstCode})`
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
            },
            measureClassDisplay: function() {
                if (this.currentSection) {
                    if (this.currentSection.dstHandicap) {
                        return '<span class="label label-handicap">Handicapkompenserende indsats</span>'
                    } else {
                        return '<span class="label label-forebyggende">Forebyggende foranstaltning</span>'
                    }
                }
            }
        },
        methods: {
            updateAppropriations: function(payload) {
                if (!payload.section) {
                    return false
                } 
                this.currentSectionId = payload.section
                this.fetchAppropriations(this.buildFilterString(payload.section, payload.to_date, payload.from_date))
                .then(res => {
                    this.appropriationlist = this.sanitizeAppropriationData(res)
                })
                .catch(err => {
                    console.error(err)
                })
            },
            buildFilterString: function(section_id, to_date, from_date) {
                const from = from_date ? from_date : 'None'
                const filter = `section:"${section_id}", dstDate:"[\\"${from}\\",\\"${to_date}\\"]"` // Remember the double escape characters `\\` to make django/GraphQL request work
                return filter
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
    .label-handicap {
        color: var(--grey10);
        background-color: var(--warning);
    }
    .label-forebyggende {
        color: var(--grey0);
        background-color: var(--primary);
    }
</style>