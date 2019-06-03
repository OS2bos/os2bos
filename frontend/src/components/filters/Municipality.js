import axios from '../http/Http.js'
import store from '../../store.js'

function id2name(id) {
    const muni_list = store.getters.getMunis
    let muni = muni_list.find(function(element) {
        return element.id === id;
    })
    return muni.name
}

export {
    id2name
}