/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


function json2js(jsondatetime) {
    if (jsondatetime) {
        const dt = new Date(jsondatetime)
        return `${ dt.getDate() }. ${ strMonth(dt.getMonth()) } ${ dt.getFullYear() }, ${ leadZero(dt.getHours()) }:${ leadZero(dt.getMinutes()) }`
    } else {
        return '-'
    }
}

function json2jsDate(jsondatetime) {
    if (jsondatetime) {
        const dt = new Date(jsondatetime)
        return `${ dt.getDate() }. ${ strMonth(dt.getMonth()) } ${ dt.getFullYear() }`
    } else {
        return '-'
    }
}

function json2jsEpoch(jsondatetime) {
    if (jsondatetime) {
        const dt = new Date(jsondatetime)
        return dt.getTime()
    } else {
        return false
    }
}

function epoch2DateStr(epoch) {
    if (epoch) {
        const dt = new Date(epoch)
        return `${ dt.getFullYear() }-${ leadZero(dt.getMonth()+1)}-${ leadZero(dt.getDate()) }`
    } else {
        return false
    }
}

function inEighteenYears() {
    const dt = new Date()
    let year_now = dt.getFullYear()
    let year_future = year_now + 18
    const future_dt = new Date().setFullYear(year_future)
    return epoch2DateStr(future_dt)
}

function tenYearsAgo() {
    const dt = new Date()
    let year_now = dt.getFullYear()
    let year_past = year_now - 10
    const past_dt = new Date().setFullYear(year_past)
    return epoch2DateStr(past_dt)
}

function leadZero(number) {
    if (number < 10) {
        return `0${ number }`
    } else {
        return number
    }
}

function strMonth(month_index) {
    const months = [
        'jan', 'feb', 'mar', 'apr', 'maj', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'
    ]
    return months[month_index]
}

export {
    json2js,
    json2jsDate,
    json2jsEpoch,
    epoch2DateStr,
    inEighteenYears,
    tenYearsAgo
}