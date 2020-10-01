<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <div class="popover" v-if="condition">
        <div class="popover-body">
            <slot></slot>
        </div>
    </div>

</template>


<script>
    export default {
        props: [
            'condition'
        ]
    }
</script>


<style>

    .popover {
        position: relative;
    }

    .popover-body {
        display: block;
        position: absolute;
        background-color: var(--warning);
        color: hsl(var(--color3), 100%, 20%);
        padding: .5rem 1rem;
        line-height: 1.25;
        bottom: .5rem;
        left: 0;
        right: 0;
        height: auto;
        width: 100%;
        min-width: 12rem;
        z-index: 100;
        box-shadow: .25rem .25rem .5rem hsla(0,0%,0%,.2);
        white-space: normal;
        border-radius: .125rem;
    }

    .popover::after {
        content: '';
        display: block;
        position: absolute;
        left: 1rem;
        bottom: -.5rem;
        height: 1rem;
        width: 1.5rem;
        clip-path: polygon(0 0, 100% 0, 50% 100%);
        z-index: 100;
        background-color: var(--warning);
    }

</style>