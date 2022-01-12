<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <section class="export-list">

        <header class="case-search-header">
            <h1>Dataudtræk</h1>
        </header>
        
        <form @submit.prevent>
            <fieldset class="filter-fields">
                <div class="filter-field">
                    <label for="preview-mode">Visning</label>
                    <!-- TODO: This list-picker should v-model some piece of
                               data that represents which cutoff date we want
                               to use in our API call -->
                    <list-picker 
                        :dom-id="'preview-mode'"
                        :list="previewModes"
                        @selection="filterByCutoff"
                        :selected-id="now"
                        display-key="label"
                        :disable-null-option="true"
                    />
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
            
        <!-- TODO: 47446 Activities that are comprised of several "partial"
                   activities (e.g. adjustments etc) should be rendered as
                   accordions in the data-grid below, as is the case elsewhere
                   in the system -->
                   
        <!-- TODO: 47442 If it's decided that this view should support the display
                   of nodes that have changed since the specified date *as well
                   as* nodes that HAVEN'T changed since that date, we need some
                   styling to visually distinguish the two in the data-grid
                   below -->
        <data-grid
            ref="data-grid"
            :data-list="appropriationlist"
            :columns="columns"
            :selectable="false">

            <p slot="datagrid-header">
                <span v-html="currentSectionDisplay"></span>
                <br>
                <span v-html="numberOfCPRsDisplay"></span>
            </p>

        </data-grid>
        
        <!-- TODO: 47444/47445 Insert components/buttons to trigger simulated and real export
                   right about here -->
    </section>

</template>

<script>
    import ListPicker from '../forms/ListPicker.vue'
    import DataGrid from '../datagrid/DataGrid.vue'
    import axios from '../http/Http.js'

    export default {
        components: {
            ListPicker,
            DataGrid
        },
        data: function () {
            return {
                now: Date.now(),
                cutoffDate: null,
                sectionlist: [],
                appropriationlist: [],
                currentSection: null,
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
                    // TODO: 47435 Add a column for the DST code
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
                        title: 'Startdato'
                    },
                    {
                        key: 'main_activity_enddate',
                        title: 'Slutdato'
                    }
                ],
                previewModes: []
            }
        },
        computed: {
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
            filterByCutoff: function() {
                console.log('filter stuff by cutoff date')
            },
            filterBySection: function(section_id) {
                if (section_id) {
                    this.currentSection = section_id
                    this.fetchAppropriations(section_id)
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
            fetchAppropriations: function(section_id) {
                return axios.post('/graphql/', { query: `
                    {
                        appropriations(section:"${section_id}") {
                            edges {
                                node {
                                    pk,
                                    sbsysId,
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
                        main_activity_enddate: activity_meta.endDate
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
                console.log(sorted_by_start, sorted_by_end)
                return {
                    pk: sorted_by_start[0].node.pk,
                    name: sorted_by_start[0].node.details.name,
                    startDate: sorted_by_start[0].node.startDate,
                    endDate: sorted_by_end[0].node.endDate,
                }
            }
            
                // Since we can't have bi-directional pagination in GraphQL
                // (it's in the spec, albeit in other words), we need to manually
                // work out whether we have a previous page to "go back to"
                // (pageInfo.hasPreviousPage will always be false whenever
                // we're using the `first` argument, even if a previous
                // page exists). Therefore, we maintain a "stack" of cursors
                // to which we push a cursor when paginating forwards, and
                // pop a cursor when paginating backwards. We know that if the
                // stack is empty, we must be on page 1. If that's the case,
                // don't render a "go back" button. If we have more than 0 cursors,
                // do render such a button. When paginating, always use the cursor
                // at the top of the stack, but if we're paginating backwards,
                // pop the last item (don't use it) before picking the topmost
                // cursor.
                
                // Links that describe the issue outlined above:
                // https://gitlab.com/gitlab-org/gitlab-foss/-/issues/62787
                // https://engineering.dubsmash.com/bi-directional-pagination-using-graphql-relay-b523c919c96
                
                // TODO: Note that the implementation of the logic described
                // above is still incomplete, since we store a cursor already
                // at page load, and it "takes an extra click" to change direction
                
                
                // TODO: 47437 Use the date as some sort of filter argument in the
                // `appropriations` field below. Awaiting the name of said filter
                // in the backend
                
                // TODO: 47435 Add a field for the DST code at sections.edges.node
                // level (next to "paragraph")
                

        },
        created: function() {

            // Fetch a list of sections for the filter dropdown
            this.fetchSections([], false)
            .then(res => {
                this.sectionlist = res
            })
            
            Promise.resolve() // TODO: 47436/47437 Replace with real endpoint to retrieve/determine export dates
            .then(() => {
                this.previewModes = [
                    {
                        id: 0,
                        label: 'Alle ændringer i systemets levetid' 
                    },
                    {
                        id: this.now,
                        label: 'Ændringer siden seneste skæringsdato'
                    }
                ]
            })
        }
    }
    
</script>

<style>
    .export-list {
        padding: 0 2rem 2rem;
    }
    .export-list .filter-fields {
        display: flex;
        flex-flow: row nowrap;
    }
    .export-list .filter-field {
        margin-right: 1rem;
    }
</style>