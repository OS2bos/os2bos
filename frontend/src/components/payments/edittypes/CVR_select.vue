<template>
    <div class="cvr-search">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <fieldset>
                <label for="cvr-search-input">Find CVR/P-nr.</label>
                <input type="search" v-model="search_input" @input="search" id="cvr-search-input">
                <ul class="cvr-search-result" v-if="search_results.length > 0">
                    <li v-for="s in search_results" :key="s.cvr_number">
                        <button class="cvr-select-btn" @click="select_item(s)" type="button">
                            <dl>
                                <dt>CVR/P-nr</dt>
                                <dd>{{ s.cvr_number }}</dd>
                                <dt>Navn</dt>
                                <dd>{{ s.name }}</dd>
                            </dl>
                        </button>
                    </li>
                </ul>
            </fieldset>
            <p>
                <a href="https://datacvr.virk.dk/data/?language=da" target="_blank">Søg på Virk.dk</a>
            </p>
        </div>
        <div v-if="service_provider">
            <dl>
                
                <dt>Navn</dt>
                <dd><strong>{{ service_provider.name }}</strong></dd>
                <dt>CVR/P-nr</dt>
                <dd>{{ service_provider.cvr_number }}</dd>
                <dt>Adresse</dt>
                <dd>
                    {{ service_provider.street }} {{ service_provider.street_number }}<br> 
                    {{ service_provider.zip_code }}
                </dd>
                <dt>Virksomhedsstatus</dt>
                <dd>{{ service_provider.status }}</dd>
            </dl>
        </div>
        <p v-else>
            Leverandør ukendt
        </p>
    </div>
</template>

<script>
import axios from '../../http/Http.js'
import Timeout from '../../mixins/Timeout.js'

export default {
    mixins: [
        Timeout
    ],
    data: function() {
        return {
            search_results: [],
            search_input: null,
            service_provider: null
        }
    },
    watch: {
        service_provider: function(new_sp, old_sp) {
            if (new_sp !== old_sp) {
                this.$store.commit('setPaymentPlanProperty', { 
                    prop: 'recipient_name',
                    val: new_sp.name
                })
                this.$store.commit('setPaymentPlanProperty', { 
                    prop: 'recipient_id',
                    val: new_sp.cvr_number
                })
                this.$store.commit('setPaymentPlanProperty', { 
                    prop: 'payment_method',
                    val: 'INVOICE'
                })
            }
        }
    },
    methods: {
        fetchData: function(query) {
            axios.get(`service_providers/fetch_serviceproviders_from_virk/?search_term=${ query }`)
            .then(res => {
                console.log(res.data)
                this.search_results = res.data
            })
        },
        search: function() {
            if (this.search_input !== '') {
                this.fetchData(this.search_input)
            } else {
                this.search_results = []
            }
        },
        select_item: function(item) {
            this.search_input = ''
            this.search_results = []
            this.service_provider = item
        }
    },
    created: function() {
        // Set debounce on methods that are likely to be fired too often
        // (ie. while a user is typing into an input field)
        this.search = this.debounce(this.search, 400)
    }
}
</script>

<style>

    .cvr-search {
        position: relative;
    }

    .cvr-search-result {
        list-style: none;
        margin: 0;
        padding: 0;
        background-color: white;
        position: absolute;
        top: 4rem;
        left: 0;
        z-index: 10;
    }

    .cvr-search-result li p {
        margin: 0;
    }

    .cvr-select-btn {
        border: none;
        height: auto;
        width: 100%;
        display: block;
        padding: .5rem 1rem;
        text-align: left;
    }

    .cvr-search-result dt {
        padding-top: .25rem;
    }

</style>