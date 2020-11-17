<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <section class="case-search">

        <header class="case-search-header">
            <h1>Sager</h1>
            <button v-if="user_can_edit === true" class="create" @click="$router.push('/case-create/')">+ Tilknyt hovedsag</button>
        </header>
        
        <case-search />

        <case-list />

    </section>

</template>

<script>
import PermissionLogic from '../mixins/PermissionLogic.js'
import CaseSearch from './CaseSearch.vue'
import CaseList from './CaseList.vue'

export default {
    components: {
        CaseSearch,
        CaseList
    },
    mixins: [
        PermissionLogic
    ]
}
</script>

<style>

    .case-search {
        padding: 0 2rem 2rem;
    }

    .case-search-header {
        display: flex;
        align-items: center;
    }

    .case-search .create {
        margin: 0 1rem;
    }

</style>
