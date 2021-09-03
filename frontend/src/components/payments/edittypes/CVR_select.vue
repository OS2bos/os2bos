<template>
    <div class="cvr-search">
        <div v-if="editable" class="cvr-search-widget">
            <fieldset style="margin: 0;">
                <label for="cvr-search-input">Leverandør</label>
                <input type="search" autocomplete="off" v-model="search_input" @input="search" id="cvr-search-input" placeholder="CVR/P-nr eller navn">
                <button type="button" class="cvr-search-input-clear" @click="select_item(false)" title="Fjern leverandør">
                    <i class="material-icons">close</i>
                </button>
                <ul class="cvr-search-result" v-if="search_results.length > 0">
                    <!--
                    <li>
                        <button class="cvr-select-btn" type="button" @click="select_item(false)">
                            <p class="title"><strong>Ukendt leverandør</strong></p>
                        </button>
                    </li>
                    -->
                    <li v-for="s in search_results" :key="s.cvr_number">
                        <button class="cvr-select-btn" @click="select_item(s)" type="button">
                            <p class="title"><strong>{{ s.name }}</strong></p>
                            <p>{{ s.business_code_text }}</p>
                            <dl>
                                <dt>CVR/P-nr</dt>
                                <dd>{{ s.cvr_number }}</dd>
                                <dt>Adresse</dt>
                                <dd>{{ s.zip_code }} {{ s.post_district }}</dd>
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
        <warning v-else content="Ingen leverandør valgt. Denne ydelse kan kun godkendes, hvis der er valgt en leverandør."></warning>
    </div>
</template>

<script>
import axios from '../../http/Http.js'
import Timeout from '../../mixins/Timeout.js'
import Warning from '../../warnings/Warning.vue'

export default {
    mixins: [
        Timeout
    ],
    components: {
        Warning
    },
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
        },
        service_provider: function(new_val, old_val) {
            if (new_val !== old_val) {
                this.search_input = new_val.name
            }
        }
    },
    methods: {
        preFetchData: function(recipient_id) {
            if (!recipient_id) {
                return
            }
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
            .catch(err => {
                this.search_results = []
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
            this.search_input = item.name
            this.search_results = []
            this.service_provider = item
            this.$store.commit('setPaymentPlanProperty', {
                prop: 'recipient_name',
                val: item.name ? item.name : ''
            })
            this.$store.commit('setPaymentPlanProperty', {
                prop: 'recipient_id',
                val: item.cvr_number ? item.cvr_number : ''
            })
            this.$store.commit('setPaymentPlanProperty', {
                prop: 'payment_method',
                val: 'INVOICE'
            })
            this.$store.commit('setActivityProperty', {
                prop: 'service_provider',
                val: item ? item : null
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
        
    }

    .cvr-search-widget {
        position: relative;
        display: flex; 
        justify-content: space-between; 
        align-items: center;
    }

    #cvr-search-input {
        min-width: 11rem;
    }

    .cvr-search-input-clear {
        box-shadow: none;
        background-color: var(--grey0);
        border: solid 1px var(--grey3);
        border-width: 1px 1px 1px 0;
        color: var(--grey10);
        display: inline-block;
        font: inherit;
        letter-spacing: inherit;
        padding: 0.25rem 0.5rem;
        transition: all .2s;
        border-radius: 0;
        margin: 0;
        height: 2rem;
        overflow: hidden;
    }

    .cvr-search-input-clear .material-icons {
        font-size: 1.5rem;
    }

    .cvr-search-result {
        list-style: none;
        margin: 0;
        padding: 0;
        background-color: white;
        position: absolute;
        top: 3.75rem;
        left: .5rem;
        z-index: 10;
        min-width: 11rem;
        max-height: 40rem;
        overflow-y: auto;
        overflow-x: visible;
        box-shadow: var(--shadow-dim);
    }

    .cvr-select-btn {
        border: none;
        height: auto;
        width: 100%;
        display: block;
        padding: .5rem 1rem .75rem;
        text-align: left;
        border-top: solid 1px var(--grey2);
        border-radius: 0;
        color: var(--grey8);
        margin: 0;
    }

    .cvr-select-btn .title {
        color: var(--primary);
    }

    .cvr-select-btn:hover .title,
    .cvr-select-btn:focus .title {
        color: var(--grey0);
    }

    .cvr-select-btn p {
        margin: 0;
    }

    .cvr-select-btn dl {
        display: grid;
        grid-template-columns: auto auto;
        grid-template-rows: auto auto;
        grid-auto-flow: column;
    }

    .cvr-select-btn dl dt {
        margin: 0;
        padding: .5rem 0 0;
    }

    .cvr-select-change {
        box-shadow: none;
    }

    .cvr-select-change:hover,
    .cvr-select-change:focus {
        color: var(--grey10);
        box-shadow: none;
        text-decoration: underline;
    }

    .cvr-select-change .material-icons {
        font-size: 1.5rem;
        position: relative;
        bottom: .125rem;
    }

    .cvr-search .warning {
        margin-top: .5rem;
    }

</style>