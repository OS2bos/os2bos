import store from '../../store.js'

function municipalityId2name(id) {
    const muni_list = store.getters.getMunis
    if (muni_list) {
        let muni = muni_list.find(function(element) {
            return element.id === id;
        })
        return muni.name
    } else {
        return 'Ikke tilgængelig'
    }
}

function districtId2name(id) {
    const dist_list = store.getters.getDistricts
    if (dist_list) {
        let dist = dist_list.find(function(element) {
            return element.id === id;
        })
        return dist.name
    } else {
        return 'Ikke tilgængelig'
    }
}

function activityId2name(id) {
    const act_list = store.getters.getActivities
    if (id) {
        let act = act_list.find(function(element) {
            return element.id === id;
        })
        return act.name
    } else {
        return 'Ikke tilgængelig'
    }
}

function sectionId2name(id) {
    const section_list = store.getters.getSections
    if (section_list) {
        let sec = section_list.find(function(element) {
            return element.id === parseInt(id);
        })
        return `${ sec.paragraph } ${ sec.kle_number } ${ sec.text }`
    } else {
        return 'Ikke tilgængelig'
    }
}

function displayStatus(status) {
    let status_str = ''
    switch(status) {
        case 'DRAFT':
            status_str = 'kladde'
            break;
        case 'BUDGETED':
            status_str = 'forventet'
            break;
        case 'GRANTED':
            status_str = 'bevilget'
            break;
        case 'DISCONTINUED':
            status_str = 'udgået'
            break;
        default:
            status_str = 'ukendt status'
    }
    return `<span class="label label-${ status }">${ status_str }</span>`
}

function displayEffort(effort_step) {
    let effort_str = ''
    switch(effort_step) {
        case 'STEP_ONE':
            effort_str = 'Trin 1 - Tidlig indsats i almenområdet'
            break
        case 'STEP_TWO':
            effort_str = 'Trin 2 - Forebyggelse'
            break
        case 'STEP_THREE':
            effort_str = 'Trin 3 - Hjemmebaserede indsatser'
            break
        case 'STEP_FOUR':
            effort_str = 'Trin 4 - Anbringelse i slægt eller netværk'
            break
        case 'STEP_FIVE':
            effort_str = 'Trin 5 - Anbringelse i forskellige typer af plejefamilier'
            break
        case 'STEP_SIX':
            effort_str = 'Trin 6 - Anbringelse i institutionstilbud'
            break
        default:
            effort_str = 'ukendt'
    }
    return effort_str
}

export {
    municipalityId2name, 
    districtId2name,
    activityId2name,
    sectionId2name,
    displayStatus,
    displayEffort
}