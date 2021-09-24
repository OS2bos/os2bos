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
    fetchServiceProviders()
    fetchSections()
    fetchActivityDetails()
    //fetchMunicipalities()
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
            sections {
                edges {
                    node {
                        pk,
                        active,
                        text,
                        paragraph,
                        lawTextName,
                        appropriations {
                            edges {
                                node {
                                    pk
                                }
                            }
                        },
                        mainActivities {
                            pk
                        },
                        supplementaryActivities {
                            pk
                        }
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
        data.municipalities = resp.data.municipalities
        
    })
}

function endFetching() {
    if (data.sections && data.service_providers && data.activity_details && data.municipalities) {
        postMessage(data)
    }
}

function fetchServiceProviders() {
    fetch('/api/service_providers/')
        .then(response => response.json())
        .then(res => {
            data.service_providers = res
            endFetching()
        })
}

function fetchSections() {
    fetch('/api/sections/')
        .then(response => response.json())
        .then(res => {
            console.log('legacy sections', res)
            data.sections = res
            endFetching()
        })
}

function fetchActivityDetails() {
    fetch('/api/activity_details/')
        .then(response => response.json())
        .then(res => {
            console.log('legacy act details', res)
            data.activity_details = res
            endFetching()
        })
}

function fetchMunicipalities() {
    fetch('/api/municipalities/')
        .then(response => response.json())
        .then(res => {
            data.municipalities = res
            endFetching()
        })
}