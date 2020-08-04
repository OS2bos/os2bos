<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <header class="globalheader-wrapper">
        <div class="globalheader">
            <router-link to="/" class="header-link" title="Bevilling og Styring">
                <img class="global-logo" src="/logo.png" alt="">
                <span class="global-brandname">Bevilling og Styring</span>
            </router-link>
            <div class="row" style="width: auto; align-items: center;">
                <nav id="globalnav" v-if="auth" class="globalnav" aria-label="Hovedmenu">
                    <router-link to="/">Sager</router-link>
                    <router-link to="/appropriation-search/">Bevillinger</router-link>
                    <router-link to="/payments/">Betalinger</router-link>
                    <a v-if="user.profile === 'workflow_engine'" href="/api/admin/">Klassifikationer</a>
                    <a v-if="user.profile === 'admin'" href="/api/admin/">Administration</a>
                </nav>
                <user-actions />
            </div>
        </div>
        <breadcrumb />
    </header> 

</template>

<script>

    import Breadcrumb from './Breadcrumb.vue'
    import UserActions from '../auth/UserActions.vue'
    
    export default {

        components: {
            Breadcrumb,
            UserActions
        },
        computed: {
            auth: function() {
                return this.$store.getters.getAuth
            },
            user: function() {
                return this.$store.getters.getUser
            }
        }

    }

</script>

<style>

    .globalheader-wrapper {
        margin: 0 0 1rem;
    }

    .globalheader {
        display: flex;
        flex-flow: row nowrap;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem .75rem;
        background-color: var(--grey0);
        box-shadow: 0 .25rem 1rem hsla(var(--color1), 83%, 62%, .125);
        margin: 0;
    }

    .header-link {
        display: block;
        margin: 0;
        padding: 0;
        border: none !important;
        position: relative;
    }

    .global-logo {
        height: 3.5rem;
        width: auto;
        opacity: 1;
        margin: 0 .5rem 0 0;
    }

    .global-brandname {
        position: absolute;
        bottom: 0.25rem;
        left: 3.375rem;
        font-size: .9rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        white-space: nowrap;
    }

    .globalheader .globalnav {
        margin: 0 2rem;
    }

    .globalheader .globalnav > a,
    .globalheader .globalnav > a:link,
    .globalheader .globalnav > a:visited {
        display: inline-block;
        padding: .5rem;
        margin: 0 0 0 1rem;
        border: solid 1px transparent;
    }

    .globalheader .globalnav > a:hover,
    .globalheader .globalnav > a:active {
        border-bottom-color: var(--primary);
    }

    .globalheader .globalnav > a:focus {
        border-color: var(--warning);
    }

</style>
