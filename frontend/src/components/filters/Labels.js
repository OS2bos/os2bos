/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


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
    const act_list = store.getters.getActivityDetails
    if (act_list) {
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
        return `${ sec.paragraph } ${ sec.text }`
    } else {
        return 'Ikke tilgængelig'
    }
}

function userId2name(id) {
    const user_list = store.getters.getUsers
    if (user_list) {
        let user = user_list.find(function(u) {
            return u.id === parseInt(id);
        })
        return user.fullname
    } else {
        return 'Ikke tilgængelig'
    }
}

function approvalId2name(id) {
    const approval_list = store.getters.getApprovals
    if (approval_list) {
        let approval = approval_list.find(function(element) {
            return element.id === parseInt(id);
        })
        return approval.name
    } else {
        return 'Ikke tilgængelig'
    }
}

function teamId2name(id) {
    const team_list = store.getters.getTeams
    if (team_list) {
        let team = team_list.find(function(element) {
            return element.id === parseInt(id);
        })
        return {
            name: team.name,
            leader: team.leader
        }
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
        case 'EXPECTED':
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
        case 1:
            effort_str = 'Trin 1 - Tidlig indsats i almenområdet'
            break
        case 2:
            effort_str = 'Trin 2 - Forebyggelse'
            break
        case 3:
            effort_str = 'Trin 3 - Hjemmebaserede indsatser'
            break
        case 4:
            effort_str = 'Trin 4 - Anbringelse i slægt eller netværk'
            break
        case 5:
            effort_str = 'Trin 5 - Anbringelse i forskellige typer af plejefamilier'
            break
        case 6:
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
    userId2name,
    displayStatus,
    displayEffort,
    approvalId2name,
    teamId2name
}