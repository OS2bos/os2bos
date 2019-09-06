<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <!--
            <i class="material-icons" style="margin-right: .5rem;">folder_shared</i>
            <router-link :to="`/case/${ appr.case.pk }`">{{ appr.case.sbsys_id }}: {{ appr.case.name }}</router-link>
            <br>
            <i class="material-icons" style="margin-left: .75rem;">subdirectory_arrow_right</i>
            <i class="material-icons">folder_open</i>
            Foranstaltning {{ appr.sbsys_id }}
        </p>
    -->

    <nav class="breadcrumb" v-if="bc.length > 0">
        <p v-for="(b, key) in bc" :class="`crumb crumb-${key}`" :key="b[0]">
            <i v-if="key !== 0" class="material-icons">subdirectory_arrow_right</i>
            <i v-if="key === 0" class="material-icons">home</i>
            <i v-if="key === 1" class="material-icons">folder_shared</i>
            <i v-if="key === 2" class="material-icons">folder_open</i>
            <i v-if="key === 3" class="material-icons">style</i>
            <router-link :to="b.link" v-if="b.link">
                {{ b.title }}
            </router-link>
            <span v-if="!b.link">
                {{ b.title }}
            </span>
        </p>
    </nav>

</template>

<script>

    export default {

        computed: {
            bc: function() {
                return this.$store.getters.getBreadcrumb
            }
        }
        
    }
    
</script>

<style>

    .breadcrumb {
        padding: 1rem 2rem;
        background-color: var(--grey1);
    }

    .breadcrumb .crumb {
        margin: 0;
        padding: 0;
    }
    
    .breadcrumb .material-icons {
        font-size: 2rem;
    }

    .breadcrumb .crumb-1 {
        margin-left: .5rem;
    }

    .breadcrumb .crumb-2 {
        margin-left: 2.5rem;
    }

    .breadcrumb .crumb-3 {
        margin-left: 4.5rem;
    }

    .breadcrumb .crumb > a  {
        border: none;
    }

</style>
