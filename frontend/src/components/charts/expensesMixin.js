/* Copyright (C) 2022 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


export default {
    methods: {
        incrementHue: function(hue_value) {
            let new_hue = Number(hue_value)
            new_hue += 30
            if (new_hue > 360) {
                new_hue = new_hue - 360
            }
            return new_hue 
        },
        updateYear: function(year) {
            this.year = Number(year)
            this.fetchData()
        },
        updateMonth: function(month) {
            this.month = Number(month)
            this.fetchData()
        }
    }    
}