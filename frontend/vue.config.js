/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


let proxySettings = {};

if (process.env.API_SERVER) {
    console.log("Enabled API_SERVER proxy on: " + process.env.API_SERVER);
    proxySettings["/api"] = {
        target: process.env.API_SERVER,
        secure: false,
    };
}

if (process.env.IDP_SERVER) {
    console.log("Enabled IDP_SERVER proxy on: " + process.env.IDP_SERVER);
    proxySettings["/simplesaml"] = {
        target: process.env.IDP_SERVER,
        secure: false,
    };
}

if(Object.keys(proxySettings).length === 0 ) {
    proxySettings = null;
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
