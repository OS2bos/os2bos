/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


function cost2da(cost) {
    let formatted_cost = new Intl.NumberFormat(['da', 'en'], {maximumFractionDigits: 2, minimumFractionDigits: 2} ).format(cost)
    return formatted_cost
}

export {
    cost2da
}