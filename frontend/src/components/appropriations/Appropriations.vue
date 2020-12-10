<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

  <section class="appropriation-search">

      <header class="appropriation-search-header">
          <h1>Bevillinger</h1>
      </header>
      
      <appropriation-search />

      <appropriation-search-list />

  </section>

</template>

<script>
  import AppropriationSearch from './AppropriationSearch.vue'
  import AppropriationSearchList from './AppropriationSearchList.vue'

  export default {
      components: {
        AppropriationSearch,
        AppropriationSearchList
      }
  }
</script>

<style>

  .appropriation-search {
      padding: 0 2rem 2rem;
  }

  .appropriation-search-header {
      display: flex;
      align-items: center;
  }

</style>
