<template>
    <section class="case">
        <h1>Opret sag</h1>
        <form>
            <fieldset>
                <label for="inputSearch">SBSYS Hovedsag:</label>
                <input id="inputSearch" type="search" v-model="cas[0].sbsys_id">
                <button class="case-button">Hent</button>
            </fieldset>
        </form>

        <div>
            <form id="getForm" v-for="c in cas" :key="c.pk">
                <fieldset>
                    <h3>Sagspart:</h3>
                    <dl>
                        <dt>CPR-nr:</dt>
                        <dd>{{ c.cpr_no }}</dd>
                        <dt>Navn:</dt>
                        <dd>{{ c.name }}</dd>
                    </dl>
                </fieldset>

                <fieldset>
                    <h3>Familie og relationer:</h3>
                    <dl>
                        <dt>Mor:</dt>
                        <dd>{{ c.family_relations[0].name }}</dd>
                        <dt>Far:</dt>
                        <dd>{{ c.family_relations[1].name }}</dd>
                        <dt>Andre:</dt>
                        <dd>{{ c.family_relations[2].name }}</dd>
                    </dl>
                </fieldset>

                <fieldset>
                    <h3>Kommune:</h3>
                    <label for="selectField1">Betalingskommune:</label>
                    <select id="selectField1">
                        <option>{{ c.municipality.payment_municipality}}</option>
                    </select>
                </fieldset>
                <fieldset>
                    <label for="selectField2">Handlekommune:</label>
                    <select id="selectField2">
                        <option>{{ c.municipality.payment_municipality}}</option>
                    </select>
                </fieldset>
                <fieldset>
                    <label for="selectField3">Bopælsskommune:</label>
                    <select id="selectField3">
                        <option>{{ c.municipality.payment_municipality}}</option>
                    </select>
                </fieldset>

                <fieldset>
                    <h3>Målgruppe:</h3>
                    <input id="inputRadio1" type="radio" name="radioButtonSet">
                    <label for="inputRadio1">Familieafdelingen</label>
                    <input id="inputRadio2" type="radio" name="radioButtonSet">
                    <label for="inputRadio2">Handicapafdelingen</label>
                </fieldset>

                <fieldset>
                    <h3>Andet:</h3>
                    <input id="inputCheckbox1" type="checkbox" name="radioButtonSet">
                    <label for="inputCheckbox1">Integrationsindsatsen</label>
                    <input id="inputCheckbox2" type="checkbox" name="radioButtonSet">
                    <label for="inputCheckbox2">Tværgående ungeindsats</label>
                </fieldset>
                <fieldset>
                    <label for="selectField">Oprindeligt distrikt:</label>
                    <select id="selectField">
                        <option>{{ c.original_district}}</option>
                    </select>
                </fieldset>
                <fieldset>
                    <dt>Indsatstrappen:</dt>
                    <dd>{{ c.effort_stairs }}</dd>
                    <dt>Skaleringstrappe:</dt>
                    <dd>{{ c.scaling_staircase }}</dd>
                </fieldset>
                <fieldset>
                    <button @click="$router.push('assessment/${ this.c.pk }')">Vurdering</button>
                </fieldset>

                <fieldset>
                    <h3>Sagsbehandling:</h3>
                    <dl>
                        <dt>Sagsbehander:</dt>
                        <dd>{{ c.case_management.case_worker }}</dd>
                        <dt>Team:</dt>
                        <dd>{{ c.case_management.team }}</dd>
                    </dl>
                    <fieldset>
                    <label for="selectField">Distrikt:</label>
                    <select id="selectField">
                        <option>{{ c.original_district}}</option>
                    </select>
                    </fieldset>
                    <fieldset>
                        <dt>Leder:</dt>
                        <dd>{{ c.case_management.manager }}</dd>
                    </fieldset>
                </fieldset>
                <fieldset>
                    <button>Gem</button>
                </fieldset>
            </form>
        </div>
    </section>

</template>

<script>

    import axios from '../http/Http.js'

    export default {

        data: function() {
            return {
                item: null,
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
                    this.cas = res.data
                    this.$store.commit('setBreadcrumb', [
                        {
                            link: '/',
                            title: 'Mine sager'
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

    .case {
        margin: 1rem;
    }
    .case-button {
        margin-left: 1rem;
    }

</style>