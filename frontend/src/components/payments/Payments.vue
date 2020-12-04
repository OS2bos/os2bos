<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

  <section class="payment-search">

      <header class="payment-search-header">
          <h1>Betalinger</h1>
      </header>
      
      <payment-search />

      <payment-search-list />

  </section>

</template>

<script>
  import PaymentSearch from './PaymentSearch.vue'
  import PaymentSearchList from './PaymentSearchList.vue'

  export default {
    components: {
        PaymentSearch,
        PaymentSearchList
    }
  }
</script>

<style>

  .payment-search {
    padding: 0 2rem 2rem;
  }

  .payment-search-header {
      display: flex;
      align-items: center;
  }

</style>
