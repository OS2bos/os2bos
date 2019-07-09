<template>
    <div class="search" v-if="auth">
        <v-autocomplete
          class="search-bar"
          name="search" 
          type="search" 
          placeholder="Søg på cpr nr. - eks. 000000-0000" 
          v-model="item"
          @update-items="updateItems"
          :min-len="11"
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
