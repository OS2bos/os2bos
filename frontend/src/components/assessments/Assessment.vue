<template>
    <section class="assessment">
        <h1>Vurderinger</h1>
        <form>
            <fieldset>
                <label for="inputSearch">SBSYS Hovedsag:</label>
                <input id="inputSearch" type="search" v-model="cas.sbsys_id">
                <button class="assessment-button">Hent</button>
            </fieldset>
        </form>

        <div>
            <form id="getForm">
                <fieldset>
                    <h3>Sagspart:</h3>
                    <dl>
                        <dt>CPR-nr:</dt>
                        <dd>{{ cas.cpr_no }}</dd>
                        <dt>Navn:</dt>
                        <dd>{{ cas.name }}</dd>
                    </dl>
                </fieldset>

                <fieldset>
                    <label for="selectField1">Indsatstrappen:</label>
                    <select id="selectField1">
                        <option>{{ cas.effort_stairs }}</option>
                    </select>
                </fieldset>
                <fieldset>
                    <label for="selectField2">Skaleringstrappe:</label>
                    <select id="selectField2">
                        <option>{{ cas.scaling_staircase }}</option>
                    </select>
                </fieldset>

                <fieldset>
                    <label for="textArea">Bemærkning:</label>
                    <textarea id="textArea"></textarea>
                </fieldset>
            </form>

                <history/>

                <fieldset>
                    <button>Opdater</button>
                </fieldset>
        </div>
    </section>

</template>

<script>

    import History from './History.vue'
    import axios from '../http/Http.js'

    export default {

        components: {
            History
        },

        data: function() {
            return {
                cas: null
            }
        },
        methods: {
            update: function() {
                this.fetchCase(this.$route.params.id)
            },
            fetchCase: function(id) {
                axios.get('../../case-data.json')
                .then(res => {
                    this.cas = res.data[0]
                    this.$store.commit('setBreadcrumb', [
                        {
                            link: '/',
                            title: 'Mine sager'
                        },
                        {
                            link: `/case-create/`,
                            title: `Sag ${ this.cas[0].sbsys_id }`
                        }
                    ])
                })
                .catch(err => console.log(err))
            }
        },
        created: function() {
            this.update()
        }
    }
    
</script>

<style>

    .assessment {
        margin: 1rem;
    }
    .assessment-button {
        margin-left: 1rem;
    }

</style>