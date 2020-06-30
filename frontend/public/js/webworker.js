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
    fetchMunicipalities()
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
            data.sections = res
            endFetching()
        })
}

function fetchActivityDetails() {
    fetch('/api/activity_details/')
        .then(response => response.json())
        .then(res => {
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