import store from '../../store.js'

function fetchData() {
    if (window.Worker) {
        const myWorker = new Worker('/js/webworker.js')
        myWorker.postMessage('go')
        myWorker.addEventListener('message', function(ev) {
            store.commit('setSections', ev.data.sections)
            store.commit('setServiceProviders', ev.data.service_providers)
            store.commit('setActDetails', ev.data.activity_details)
            store.commit('setMunis', ev.data.municipalities)
        })
        myWorker.addEventListener('error', function(ev) {
            console.log(ev.message)
        })
    }
}    

export {
    fetchData
}