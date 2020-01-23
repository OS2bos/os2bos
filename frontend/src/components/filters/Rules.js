/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


/**
 * Check that an activity has payment type PERSON/CASH 
 * and that its starting date is no earlier than tomorrow
 * @param {object} start_date Start date for the activity
 * @param {object} method Payment method for the activity (from activity.payment_plan)
 * @returns {string} Warning text if rule is not met
 */
function checkRulePayDate(start_date, method) {
    if (method === 'CASH' && new Date(start_date).getTime() < new Date(new Date().setUTCHours(23,59))) {
        return `
            <strong>Bemærk:</strong> Betalinger med udbetalingsdato i dag eller tidligere vil ikke blive udbetalt.<br>
            Du er i gang med at oprette en ydelse med betaling tilbage i tid.
        `
    }
    return false
}


export {
    checkRulePayDate
}