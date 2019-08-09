<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <div class="search" v-if="auth">
        <v-autocomplete
          class="search-bar"
          name="search" 
          type="search" 
          placeholder="Søg på cpr nr." 
          v-model="item"
          @update-items="updateItems"
          :min-len="4"
        />
    </div>
</template>

<script>

    import axios from '../http/Http.js'
    import VAutocomplete from 'v-autocomplete'
    import 'v-autocomplete/dist/v-autocomplete.css'

    export default {

      components: {
        VAutocomplete
      },

      data: function() {
          return {
            item: null
          }
      },
      computed: {
        auth: function() {
            return this.$store.getters.getAuth
        },
        cas: function() {
            return this.$store.getters.getCase
        }
      },
      methods: {
        updateItems (query) {
          query = query || ''
          if (!query.match(/-/)) {
              let str = query.substring(6, 10).replace('', '-')
              query = query.substring(0, 6) + str
          }
          this.$router.push(`/all-cases/${ query }`)
        }
      }

    }

</script>

<style>

  .search .search-bar  {
    width: 20rem;
  }

  .search .material-icons {
    font-size: 16px;
  }

</style>
