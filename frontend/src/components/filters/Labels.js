/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import store from '../../store.js'

/**
 * Convert municipality id to human readable name
 * @param {number} id municipality ID
 * @returns {string} municipality name
 */
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

/**
 * Convert target group id to human readable name
 * @param {number} id target group ID
 * @returns {string} target group name
 */
function targetGroupId2name(id) {
    const targetGroup_list = store.getters.getTargetGroups
    if (targetGroup_list) {
        let target = targetGroup_list.find(function(element) {
            return element.id === id;
        })
        return target.name
    } else {
        return 'Ikke tilgængelig'
    }
}

/**
 * Convert district id to human readable name
 * @param {number} id distict ID
 * @returns {string} dictrict name
 */
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

/**
 * Convert effort id to human readable name
 * @param {number} id effort ID
 * @returns {string} effort name
 */
function effortId2name(id) {
    const effort_list = store.getters.getEfforts
    
    if (effort_list) {
        let effort = effort_list.find(function(element) {
            return element.id === parseInt(id)
        })
        return effort.name
    } else {
        return 'Ikke tilgængelig'
    }
}

/**
 * Convert activity id to human readable name
 * @param {number} id activity ID
 * @returns {string} activity name
 */
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

/**
 * Convert section id to human readable name
 * @param {number} id section ID
 * @returns {string} section name
 */
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

/**
 * Convert user id to human readable name
 * @param {number} id user ID
 * @returns {string} user's name
 */
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

/**
 * Convert approval id to human readable name
 * @param {number} id approval ID
 * @returns {string} approval name
 */
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

/**
 * Convert team id to human readable name
 * @param {number} id team ID
 * @returns {string} team's name
 */
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

/**
 * Return a human readable status
 * @param {string} id system status name
 * @returns {string} Readable status in Danish
 */
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

/**
 * Convert effort step id to human readable name
 * @param {number} id effort step ID
 * @returns {string} effort step name
 */
function displayEffort(id) {
    const effort_step_list = store.getters.getEffortSteps
    if (effort_step_list) {
        let effort_step = effort_step_list.find(function(e) {
            return e.id === parseInt(id);
        })
        if (effort_step) {
            return effort_step.name
        } else {
            return 'Ukendt'
        }
    } else {
        return 'Ikke tilgængelig'
    }
}

export {
    municipalityId2name,
    targetGroupId2name,
    districtId2name,
    effortId2name,
    activityId2name,
    sectionId2name,
    userId2name,
    displayStatus,
    displayEffort,
    approvalId2name,
    teamId2name
}