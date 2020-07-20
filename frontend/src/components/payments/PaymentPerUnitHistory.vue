<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <div class="prices-history" v-if="prices">
        <button type="button" @click="modal_open = !modal_open">Se priser</button>

        <form @submit.prevent="saveNewPrice" class="modal-form">
            <modal-dialog v-if="modal_open" @closedialog="cancelDialog">
                <h3 slot="header" class="prices-history-header">
                    <span>Priser</span>
                </h3>
                <div slot="body">
                    <table>
                        <thead>
                            <tr>
                                <th>Pris</th>
                                <th>Gælder fra</th>
                                <th>Gælder til</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="p in prices.rates_per_date" :key="p.start_date">
                                <td>{{ p.rate }} kr</td>
                                <td>{{ displayDate(p.start_date) }}</td>
                                <td>{{ displayDate(p.end_date) }}</td>
                            </tr>
                        </tbody>
                    </table>

                    <fieldset>
                        <div>
                            <label class="required" for="pay-cost-pr-unit">Ny enhedspris</label>
                            <input type="number" id="pay-cost-pr-unit" required step="0.01" v-model="new_price"> kr
                            <error :err-key="'rate'" />
                        </div>
                        <div>        
                            <label for="pay-cost-exec-date" class="required">Ny pris gælder fra</label>
                            <input 
                                type="date" 
                                id="pay-cost-exec-date" 
                                required 
                                v-model="new_start_date"
                                :min="today">
                            <error :err-key="'start_date'" />
                        </div>
                    </fieldset>
                </div>
                <div slot="footer">
                    <input type="submit" value="Gem">
                    <button type="button" @click="cancelDialog">
                        Annullér
                    </button>
                </div>
            </modal-dialog>
        </form>
    </div>

</template>

<script>
import ModalDialog from '../dialog/Dialog.vue'
import { json2jsDate, epoch2DateStr } from '../filters/Date.js'
import Error from '../forms/Error.vue'
import axios from '../http/Http.js'

export default {
    components: {
        ModalDialog,
        Error
    },
    data: function() {
        return {
            modal_open: false,
            new_price: null,
            new_start_date: epoch2DateStr(new Date()),
            today: epoch2DateStr(new Date())
        }
    },
    computed: {
        prices: function() {
            return this.$store.getters.getPaymentPlanProperty('price_per_unit')
        }
    },
    methods: {
        saveNewPrice: function() {
            const data = {
                amount: this.new_price,
                start_date: this.new_start_date
            }
            axios.patch(`/prices/${ this.prices.id }/`, data)
            .then(res => {
                this.modal_open = false
                this.resetValues()
                this.$store.dispatch('fetchActivity', this.$route.params.actId)
            })
            .catch(err => {
                this.$store.dispatch('parseErrorOutput', err)
            })
        },
        displayDate: function(date) {
            return json2jsDate(date)
        },
        cancelDialog: function() {
            this.modal_open = !this.modal_open
            this.resetValues()    
        },
        resetValues: function() {
            this.new_price = null
            this.new_start_date = epoch2DateStr(new Date())
        }
    }
}
</script>

<style>
    .prices-history {
        margin: .5rem 0;
    }
    .prices-history-header {
        padding: 0;
        font-size: 1.25rem;
    }
</style>