/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import './spinner.css'

/**
 * Create a GUI spinner instance. Handy for when users have to wait for something to load.
 * @returns {object} spinner instance
 * @kind function
 */
const spinner = function() {

    const spin_el = document.createElement('div')
    spin_el.id = 'spinner'
    spin_el.role = 'alert'

    const
        /**
         * Test if a spinner is already in the GUI
         * @memberof spinner
         * @returns {boolean} True if a spinner element is in the DOM
         * @kind function
         */
        testSpin = function() {
            if (document.getElementById('spinner')) {
                return true
            } else {
                return false
            }
        },
        /**
         * Start a GUI spinner
         * @memberof spinner
         * @kind function
         */
        spinOn = function() {
            if (!testSpin()) {
                document.body.appendChild(spin_el)
            }
        },
        /**
         * Stop a GUI spinner
         * @memberof spinner
         * @kind function
         */
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