<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <section class="activities">
        <button class="activities-create-btn" title="Ny aktivitet" @click="createAct()">+ Tilføj ydelse</button>
        <div class="grid-container">
          <div class="grid-box" v-for="a in acts" :key="a.pk">
            <dl>
              <dt>Status</dt>
              <dd><span :class="`status-${ a.status }`">{{ a.status }}</span></dd>
              <dt>Ydelse</dt>
              <dd><router-link :to="`/activity/${ a.pk }`">{{ a.activity }}</router-link></dd>
              <dt>Udbetales til</dt>
              <dd>{{ a.payment.payee.name }}</dd>
              <dt>CPR-nr</dt>
              <dd>300178-1207</dd>
              <dt>Økonomi</dt>
              <dd>{{ a.payment.total_amount }}</dd>
              <dt>Start</dt>
              <dd>{{ new Date(a.startdate).toLocaleDateString() }}</dd>
              <dt>Slut</dt>
              <dd>{{ new Date(a.enddate).toLocaleDateString() }}</dd>
            </dl>
          </div>
        </div>
          <div class="box-sum">
            <dl>
              <dt>Pr. måned</dt>
              <dd>{{ total_amounts }} kr.</dd>
              <dt>Samlet sum</dt>
              <dd>{{ total_amounts }} kr.</dd>
            </dl>
          </div>
    </section>

</template>

<script>

    import axios from '../http/Http.js'

    export default {

        props: [
            'apprId'
        ],
        data: function() {
            return {
                acts: null   
            }
        },
        computed: {
            total_amounts: function() {
                function getTotal(total, act) {
                    console.log(total)
                    console.log(act.payment.total_amount)
                    return total + act.payment.total_amount
                }
                if (this.acts) {
                    return this.acts.reduce(getTotal, 0)
                }
            }
        },
        methods: {
            fetchActivities: function(appropriation_id) {
                axios.get('../../activity-list-data.json')
                .then(res => {
                    this.acts = res.data
                })
                .catch(err => console.log(err))
            },
            createAct: function() {
                axios.post('/') // POST new empty activity
                .then(res => {
                    this.$router.push(`/activity/${ res.data.pk }`) // Navigate to new activity page
                })
                .catch(err => console.log(err))
            }
        },
        created: function() {
            if (this.apprId) {
                this.fetchActivities(this.apprId)
            }
        }
    }
    
</script>

<style>

    .activities {
        margin: 1rem;
    }

    .activities-header {
        display: flex;
        flex-flow: row nowrap;
        justify-content: flex-start;
        align-items: center;
    }

    .activities-create-btn {
        margin: 0 0 1rem;
    }

    .activities .status-Bevilget {
        background-color: var(--success);
        color: white;
        padding: .25rem;
    }

    .activities .status-Forventet {
        background-color: var(--warning);
        color: white;
        padding: .25rem;
    }

    .activities .grid-container {
        display: grid;
        grid-template-columns: auto auto auto auto;
    }

    .grid-box {
        border: solid 1px var(--grey1);
        padding: .5rem 1rem;
        margin: 1px;
    }

    .total-sum{
        background-color: green;
        color: white;
        padding: .25rem;
    }

</style>
