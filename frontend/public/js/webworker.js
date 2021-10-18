/* Copyright (C) 2020 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

onmessage = function(e) {
    if (e.data === 'go') {
        startFetching()
    }
}

let data = {
    sections: null,
    service_providers: null,
    activity_details: null,
    municipalities: null
}

function startFetching() {
    fetchSections()
    const qry = {
        query: `{
            municipalities {
                edges {
                    node {
                        pk,
                        name,
                        active
                    }
                }
            },
            activityDetails {
                edges {
                     node {
                        pk,
                        active,
                        activityId,
                        description,
                        maxToleranceInDkk,
                        maxToleranceInPercent,
                        name,
                        mainActivities {
                            edges {
                                node {
                                    pk
                                }
                            }
                        },
                        mainActivityFor {
                            edges {
                                node {
                                    pk
                                }
                            }
                        },
                        supplementaryActivityFor {
                            edges {
                                node {
                                    pk
                                }
                            }
                        },
                        serviceProviders {
                            edges {
                                node {
                                    pk
                                }
                            }
                        }
                    } 
                }
            },
            serviceProviders {
                edges {
                    node {
                        pk,
                        name,
                        active,
                        businessCode,
                        businessCodeText,
                        cvrNumber,
                        postDistrict,
                        status,
                        street,
                        streetNumber,
                        vatFactor,
                        zipCode
                    }
                }
            }
        }`
    }
    fetch('/api/graphql/', {
        method: 'POST',
        body: JSON.stringify(qry),
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(resp => {
        data.municipalities = resp.data.municipalities.edges.map(muni => {
            return {
                id: muni.node.pk,
                name: muni.node.name,
                active: muni.node.active
            }
        })
        data.activity_details = resp.data.activityDetails.edges.map(actd => {
            return {
                id: actd.node.pk,
                name: actd.node.name,
                active: actd.node.active,
                activity_id: actd.node.activityId,
                description: actd.node.description,
                max_tolerance_in_percent: actd.node.maxToleranceInPercent,
                max_tolerance_in_dkk: actd.node.maxToleranceInDkk,
                main_activities: actd.node.mainActivities.edges.map(mainact => mainact.node.pk),
                main_activity_for: actd.node.mainActivityFor.edges.map(mainactfor => mainactfor.node.pk),
                service_providers: actd.node.serviceProviders.edges.map(sp => sp.node.pk),
                supplementary_activity_for: actd.node.supplementaryActivityFor.edges.map(supplactfor => supplactfor.node.pk)
            }
        })
        data.service_providers = resp.data.serviceProviders.edges.map(sp => {
            return {
                active: sp.node.active,
                business_code: sp.node.businessCode,
                business_code_text: sp.node.businessCodeText,
                cvr_number: sp.node.cvrNumber,
                id: sp.node.pk,
                name: sp.node.name,
                post_district: sp.node.postDistrict,
                status: sp.node.status,
                street: sp.node.street,
                street_number: sp.node.streetNumber,
                vat_factor: sp.node.vatFactor,
                zip_code: sp.node.zipCode
            }
        })
        endFetching()
    })
}

function endFetching() {
    if (data.sections && data.service_providers && data.activity_details && data.municipalities) {
        postMessage(data)
    }
}

function fetchSections() {
    fetch('/api/sections/')
        .then(response => response.json())
        .then(res => {
            data.sections = res
            endFetching()
        })
}
