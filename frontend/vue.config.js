/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


let proxySettings = null;

if (process.env.API_SERVER) {
    let server = {
        target: process.env.API_SERVER,
        secure: false,
    };

    proxySettings = {
        "/api": server,
    };
}

module.exports = {
    devServer: {
        proxy: proxySettings,
        disableHostCheck: true,
    },
    configureWebpack: config => {
        if (process.env.NODE_ENV === 'production') {
            config.performance = {
                hints: 'warning'
            }
        }
    }
};
