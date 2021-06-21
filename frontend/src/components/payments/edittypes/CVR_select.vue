<template>
    <div class="cvr-search">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <fieldset>
                <label for="cvr-search-input">Find CVR/P-nr.</label>
                <input type="search" v-model="search_input" @input="search" id="cvr-search-input">
                <ul class="cvr-search-result" v-if="search_results.length > 0">
                    <li v-for="s in search_results" :key="s.id">
                        <button class="cvr-select-btn" @click="select_item(s)" type="button">
                            <dl>
                                <dt>CVR/P-nr</dt>
                                <dd>{{ s.id }}</dd>
                                <dt>Navn</dt>
                                <dd>{{ s.name }}</dd>
                                <dt>Adresse</dt>
                                <dd>{{ s.address }}</dd>
                            </dl>
                        </button>
                    </li>
                    <li>
                        <button class="cvr-select-btn" @click="select_item({name: 'Ukendt leverandør', id: 0})" type="button">
                            Ukendt leverandør
                        </button>
                    </li>
                </ul>
            </fieldset>
            <p>
                <a href="https://datacvr.virk.dk/data/?language=da" target="_blank">Søg på Virk.dk</a>
            </p>
        </div>
        <div v-if="selected && selected.id !== 0">
            <dl>
                <dt>CVR/P-nr</dt>
                <dd>{{ selected.id }}</dd>
                <dt>Navn</dt>
                <dd>{{ selected.name }}</dd>
                <dt>Adresse</dt>
                <dd>{{ selected.address }}</dd>
            </dl>
        </div>
        <p v-if="selected && selected.id === 0">
            Ukendt leverandør valgt
        </p>
    </div>
</template>

<script>
export default {
    data: function() {
        return {
            search_results: [],
            search_input: null,
            selected: null,
            fake_data: [
                {
                    id: 83987673,
                    name: 'Fiktivt firma',
                    address: 'Fiktivvej 1234, 1000 Fiktivby'
                },
                {
                    id: 87665222,
                    name: 'Et andet firma',
                    address: 'Something Something 1234, 2000 Xåby'
                }
            ]
        }
    },
    computed: {
        
    },
    methods: {
        search: function() {
            if (this.search_input !== '') {
                this.search_results = this.fake_data
            } else {
                this.search_results = []
            }
        },
        select_item: function(item) {
            this.search_input = ''
            this.search_results = []
            this.selected = item
        }
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