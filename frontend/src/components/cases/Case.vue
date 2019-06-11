<template>

    <section class="case" v-if="cas">

        <header class="case-header">
            <h1 style="padding: 0;">
                <i class="material-icons">folder_shared</i>
                Hovedsag {{ cas.sbsys_id }}
            </h1>
            <button @click="edit_mode = !edit_mode">Redigér</button>
        </header>

        <div class="case-info" v-if="!edit_mode">
            <dl>
                <dt>Sagspart (CPR, navn)</dt>
                <dd>{{ cas.cpr_number }}, {{ cas.name }}</dd>
                <dt>Indsatstrappen:</dt>
                <dd>ikke implementeret</dd>
                <dt>Skaleringstrappe:</dt>
                <dd>ikke implementeret</dd>
            </dl>
            <dl>
                <dt>Distrikt</dt>
                <dd>{{ displayDistrictName(cas.district) }}</dd>
                <dt>Målgruppe</dt>
                <dd>
                    <span v-if="cas.target_group === 'DISABILITY_DEPT'">
                        Handicapafdelingen
                    </span>
                    <span v-if="cas.target_group === 'FAMILY_DEPT'">
                        Familieafdelingen
                    </span>
                </dd>
                <template v-if="cas.cross_department_measure || cas.refugee_integration">
                    <dt>Indsatser</dt>
                    <dd>
                        <div v-if="cas.cross_department_measure">
                            Tværgående ungeindsats
                        </div>
                        <div v-if="cas.refugee_integration">
                            Integrationsindsatsen
                        </div>
                    </dd>
                </template>
            </dl>
            <dl>
                <dt>Sagsbehander</dt>
                <dd>{{ cas.case_worker }}</dd>
                <dt>Team</dt>
                <dd>ikke implementeret</dd>
                <dt>Leder</dt>
                <dd>ikke implementeret</dd>
            </dl>
            <dl>
                <dt>Betalingskommune</dt>
                <dd>{{ displayMuniName(cas.paying_municipality) }}</dd>
                <dt>Handlekommune</dt>
                <dd>{{ displayMuniName(cas.acting_municipality) }}</dd>
                <dt>Bopælsskommune</dt>
                <dd>{{ displayMuniName(cas.residence_municipality) }}</dd>
            </dl>
        </div>

        <case-edit :case-obj="cas" v-if="edit_mode" @close="reload()" />

        <appropriations :case-id="cas.id" />

    </section>

</template>

<script>

    import CaseEdit from './CaseEdit.vue'
    import Appropriations from '../appropriations/AppropriationList.vue'
    import axios from '../http/Http.js'
    import { municipalityId2name, districtId2name } from '../filters/Labels.js'

    export default {

        components: {
            CaseEdit,
            Appropriations
        },
        
        data: function() {
            return {
                cas: null,
                edit_mode: false
            }
        },
        methods: {
            update: function() {
                this.fetchCase(this.$route.params.id)
            },
            fetchCase: function(id) {
                axios.get(`/cases/${id}/`)
                .then(res => {
                    this.cas = res.data
                    this.$store.commit('setBreadcrumb', [
                        {
                            link: '/',
                            title: 'Mine sager'
                        },
                        {
                            link: false,
                            title: `${ this.cas.sbsys_id}, ${ this.cas.name}`
                        }
                    ])
                })
                .catch(err => console.log(err))
            },
            reload: function() {
                this.edit_mode =  false
                this.update()
            },
            displayMuniName: function(id) {
                return municipalityId2name(id)
            },
            displayDistrictName: function(id) {
                return districtId2name(id)
            }
        },
        created: function() {
            this.update()
        }
        
    }
    
</script>

<style>

    .case {
        margin: 1rem 2rem;
    }

    .case-header {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
    }

    .case-header > button {
        margin: 1rem;
    }

    .case-info {
        display: grid; 
        grid-template-columns: auto auto auto auto;
        grid-gap: 3rem;
        justify-content: start;
        background-color: var(--grey1);
        padding: 1.5rem 2rem 2rem;
    }

</style>
