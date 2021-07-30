<template>
    <div class="cvr-search">
        <div v-if="editable && input_visible" class="cvr-search-widget">
            <fieldset>
                <label for="cvr-search-input">Find virksomhed</label>
                <input type="search" v-model="search_input" @input="search" id="cvr-search-input" placeholder="CVR/P-nr eller navn">
                <ul class="cvr-search-result" v-if="search_results.length > 0">
                    <li v-for="s in search_results" :key="s.cvr_number">
                        <button class="cvr-select-btn" @click="select_item(s)" type="button">
                            <p class="title"><strong>{{ s.name }}</strong></p>
                            <p v-if="s.business_code_text">{{ s.business_code_text }}</p>
                            <dl v-if="s.zip_code">
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
                <dt>Firmanavn</dt>
                <dd>
                    <strong>{{ service_provider.name }}</strong>
                    <button type="button" class="link-btn cvr-select-change" v-if="editable && service_provider && !input_visible" @click="input_visible = !input_visible">
                        <span class="material-icons">edit</span>
                        Skift
                    </button>
                </dd>
                <template v-if="service_provider.business_code_text">
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
                </template>
            </dl>
        </div>
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
            service_provider: null,
            input_visible: false,
            fake_service_provider: {
                name: 'Ukendt leverandør',
                cvr_number: '00000000'
            }
        }
    },
    watch: {
        dataRecipientId: function(new_id) {
            this.preFetchData(new_id)
        }
    },
    methods: {
        preFetchData: function(recipient_id) {
            if (!recipient_id) {
                this.input_visible = true
                return
            }
            if (recipient_id === this.fake_service_provider.cvr_number) {
                this.service_provider = this.fake_service_provider
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
                let selectables = res.data
                selectables.unshift(this.fake_service_provider)
                this.search_results = selectables
            })
            .catch(err => {
                this.search_results = [this.fake_service_provider]
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
            console.log('old reid', this.dataRecipientId)
            console.log('selecting item', item, this.service_provider)
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
            this.input_visible = false
            console.log('selected item', this.service_provider)
            console.log('new reid', this.dataRecipientId)
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
        border: solid 1px var(--grey2);
        padding: 0 1rem;
    }

    #cvr-search-input {
        min-width: 11rem;
    }

    .cvr-search-result {
        list-style: none;
        margin: 0;
        padding: 0;
        background-color: white;
        position: absolute;
        top: 3.75rem;
        left: 1rem;
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

</style>