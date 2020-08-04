/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


/**
 * Check that an activity has payment method PERSON/CASH
 * and that its starting date is no earlier than tomorrow
 * @param {string} start_date Start date string for the activity
 * @param {string} method Payment method string for the activity (from activity.payment_plan)
 * @returns {string} Warning text if rule is not met
 */
function checkRulePayDate(start_date, method) {
    let split_date = new Date(new Date().setDate(new Date().getDate() + 2))
    split_date.setHours(0, 0, 0) 
    if (method === 'CASH' && new Date(start_date).getTime() < split_date.getTime()) {
        return `
            <strong>Bemærk:</strong> Betalinger med udbetalingsdato i morgen eller tidligere vil ikke blive udbetalt.
        `
    }
    return false
}

export {
    checkRulePayDate
}