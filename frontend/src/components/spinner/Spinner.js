/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import './spinner.css'

const spinner = function() {

    const spin_el = document.createElement('div')
    spin_el.id = 'spinner'
    spin_el.role = 'alert'

    const
        testSpin = function() {
            if (document.getElementById('spinner')) {
                return true
            } else {
                return false
            }
        },
        spinOn = function() {
            if (!testSpin()) {
                document.body.appendChild(spin_el)
            }
        },
        spinOff = function() {
            if (testSpin()) {
                document.body.removeChild(spin_el)
            }
        }

    return {
        spinOn,
        spinOff
    }
}

export default spinner()