<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

      <select :id="domId" class="listpicker" @change="emitChange" v-model="selection">
          <option :value="null">---</option>
          <option 
              v-for="i in intervals" 
              :value="i.id" 
              :key="i.id">
              {{ i }}
          </option>
      </select>

</template>

<script>

    export default {

        props: {
          domId: String,
          selectedId: Number,
          interval: [Array, Boolean],
          default: {
              type: Number,
              default: null
          }
        },
        data: function(){
            return {
                selection: null,
                intervals: {
                  this_week: "Denne uge",
                  last_week: "Sidste uge",
                  next_week: "Næste uge",
                  this_month: "Denne måned",
                  last_month: "Sidste måned",
                  next_month: "Næste måned",
                  this_year: "Dette år",
                  between_dates: "Til og fra dato"
                }
            }
        },
        computed: {
          timeinterval: function () {
            let interval = this.interval
            if(interval) {
              this.next_week = moment().add(1, 'days').calendar();
            }
          }
        },
        watch: {
            query: function() {
                this.update()
            }
        },
        methods: {

        }
    }

</script>

<style>

    .listpicker {
        width: 100%;
    }

</style>