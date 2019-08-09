<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <header>
        <div class="globalheader">
            <h1 title="Ballerup Bevillingsplatformen">
                <router-link to="/" class="header-link">
                    <img class="global-logo" src="/logo.png" alt="" />
                    <span class="global-brandname">Bevillingsplatformen</span>
                </router-link>
            </h1>
            <div class="row" style="width: auto; align-items: center;">
                <nav v-if="auth" class="globalnav">
                    <router-link to="/my-cases/">Mine sager</router-link>
                    <router-link to="/all-cases/">Find sag</router-link>
                    <!-- <router-link to="/data-view/">Find ydelse</router-link> -->
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
            }
        }

    }

</script>

<style>

    .globalheader {
        display: flex;
        flex-flow: row nowrap;
        justify-content: space-between;
        align-items: center;
        padding: 2rem;
        background-color: var(--grey0);
    }

    .globalheader > h1 {
        margin: 0;
        padding: 0;
        display: block;
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
    }

    .globalheader .globalnav {
        margin: 0 2rem;
    }

    .globalheader .globalnav > a {
        display: inline-block;
        padding: .5rem;
        margin: 0 0 0 1rem;
    }

</style>
