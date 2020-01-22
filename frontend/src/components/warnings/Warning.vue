<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <p class="warning" v-if="content">
        <span class="warning-icon">⚠</span>
        <span v-html="content"></span>
    </p>

</template>


<script>
    export default {
        props: [
            'content'
        ]
    }
</script>


<style>

    .warning {
        background-color: var(--warning);
        color: hsl(var(--color3), 100%, 20%);
        padding: 1rem 1.5rem;
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
        margin: 0 0 1rem;
    }

    .warning-icon {
        font-size: 2rem;
        margin: 0 1rem 0 0;
    }

</style>