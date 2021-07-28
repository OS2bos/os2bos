<template>
    <div class="cvr-search">
        <div v-if="editable" style="display: flex; justify-content: space-between; align-items: center;">
            <fieldset>
                <label for="cvr-search-input">Find CVR/P-nr.</label>
                <input type="search" v-model="search_input" @input="search" id="cvr-search-input">
                <ul class="cvr-search-result" v-if="search_results.length > 0">
                    <li v-for="s in search_results" :key="s.cvr_number">
                        <button class="cvr-select-btn" @click="select_item(s)" type="button">
                            <p class="title"><strong>{{ s.name }}</strong></p>
                            <dl>
                                <dt>Adresse</dt>
                                <dd>{{ s.zip_code }} {{ s.post_district }}</dd>
                                <dt>CVR/P-nr</dt>
                                <dd>{{ s.cvr_number }}</dd>
                                <dt>Branche</dt>
                                <dd>{{ s.business_code_text }}</dd>
                            </dl>
                        </button>
                    </li>
                </ul>
            </fieldset>
            <p style="margin: 0;">
                <a href="https://datacvr.virk.dk/data/?language=da" target="_blank">Søg på Virk.dk</a>
            </p>
        </div>
        <div v-if="service_provider">
            <dl>
                <dt>Firmanavn</dt>
                <dd><strong>{{ service_provider.name }}</strong></dd>
                <dt>Branchekode</dt>
                <dd>{{ service_provider.business_code_text }}</dd>
                <dt>CVR/P-nr</dt>
                <dd>{{ service_provider.cvr_number }}</dd>
                <dt>Adresse</dt>
                <dd>
                    {{ service_provider.street }} {{ service_provider.street_number }}<br> 
                    {{ service_provider.zip_code }} {{ service_provider.post_district }}
                </dd>
                <dt>Virksomhedsstatus</dt>
                <dd style="text-transform: lowercase;">{{ service_provider.status }}</dd>
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
    props: [
        'editable',
        'dataRecipientId'
    ],
    data: function() {
        return {
            search_results: [],
            search_input: null,
            service_provider: null
        }
    },
    watch: {
        dataRecipientId: function(new_id) {
            this.preFetchData(new_id)
        }
    },
    methods: {
        preFetchData: function(recipient_id) {
            axios.get(`service_providers/fetch_serviceproviders_from_virk/?search_term=${ recipient_id }`)
            .then(res => {
                this.service_provider = res.data.find(sp => {
                    return sp.cvr_number === recipient_id
                })
            })
        },
        fetchData: function(query) {
            axios.get(`service_providers/fetch_serviceproviders_from_virk/?search_term=${ query }`)
            .then(res => {
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
            this.$store.commit('setPaymentPlanProperty', {
                prop: 'recipient_name',
                val: item.name
            })
            this.$store.commit('setPaymentPlanProperty', {
                prop: 'recipient_id',
                val: item.cvr_number
            })
            this.$store.commit('setPaymentPlanProperty', {
                prop: 'payment_method',
                val: 'INVOICE'
            })
            this.$store.commit('setActivityProperty', {
                prop: 'service_provider',
                val: item
            })
        }
    },
    created: function() {
        // Set debounce on methods that are likely to be fired too often
        // (ie. while a user is typing into an input field)
        this.search = this.debounce(this.search, 400)
        
        this.preFetchData(this.dataRecipientId)
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
        top: 3.75rem;
        left: 0;
        z-index: 10;
        min-width: 11rem;
    }

    .cvr-search-result li p {
        margin: 0;
    }

    .cvr-select-btn {
        border: none;
        height: auto;
        width: 100%;
        display: block;
        padding: .75rem 1.5rem;
        text-align: left;
        border-top: solid 1px var(--grey2);
        border-radius: 0;
        color: var(--grey8);
    }

    .cvr-select-btn .title {
        color: var(--primary);
    }

    .cvr-select-btn:hover .title,
    .cvr-select-btn:focus .title {
        color: var(--grey0);
    }

    .cvr-search-result dt {
        padding-top: .25rem;
    }

</style>