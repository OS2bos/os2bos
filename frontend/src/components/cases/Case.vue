<template>

    <section class="case" v-if="cas">

        <header class="case-header">
            <h1 style="padding: 0;">
                <i class="material-icons">folder_shared</i>
                Hovedsag {{ cas.sbsys_id }}
            </h1>
            <div v-if="!edit_mode" class="actions">
                <button @click="edit_mode = !edit_mode">Redigér</button>
                <a :href="`/api/cases/${ cas.id }/csv/`" target="_blank">Download .CSV</a>
            </div>
        </header>

        <div class="case-info" v-if="!edit_mode">
            <dl>
                <dt>Sagspart (CPR, navn)</dt>
                <dd>
                    {{ cas.cpr_number }}, {{ cas.name }}
                </dd>
                <dt>Indsatstrappen</dt>
                <dd>{{ displayEffortName(cas.effort_step) }}</dd>
                <dt>Skaleringstrappe</dt>
                <dd style="display: flex; flex-flow: row nowrap; justify-content: space-between; align-items: center;">
                    <span>{{ cas.scaling_step }}</span>
                    <router-link :to="`/case/${ cas.id }/assessment`">Se vurderinger</router-link>
                </dd>
            </dl>
            <dl>
                <dt>Målgruppe</dt>
                <dd>
                    <span v-if="cas.target_group === 'DISABILITY_DEPT'">
                        Handicapafdelingen
                    </span>
                    <span v-if="cas.target_group === 'FAMILY_DEPT'">
                        Familieafdelingen
                    </span>
                </dd>
                <template v-if="cas.target_group === 'FAMILY_DEPT'">
                    <dt>Skoledistrikt</dt>
                    <dd>{{ displayDistrictName(cas.district) }}</dd>
                </template>
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
                <template v-if="cas.note">
                    <dt>Supplerende oplysninger</dt>
                    <dd>{{ cas.note }}</dd>
                </template>
            </dl>
            <dl>
                <dt>Sagsbehander</dt>
                <dd>{{ displayUserName(cas.case_worker) }}</dd>
                <dt>Team</dt>
                <dd>{{ displayTeamName(cas.team).name }}</dd>
                <dt>Leder</dt>
                <dd>{{ displayUserName( displayTeamName(cas.team).leader ) }}</dd>
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

        <family-overview :case-id="cas.id" />

        <appropriations :case-id="cas.id" />

    </section>

</template>

<script>

    import CaseEdit from './CaseEdit.vue'
    import Appropriations from '../appropriations/AppropriationList.vue'
    import FamilyOverview from '../familyoverview/FamilyOverview.vue'
    import axios from '../http/Http.js'
    import { municipalityId2name, districtId2name, displayEffort, userId2name, teamId2name } from '../filters/Labels.js'

    export default {

        components: {
            CaseEdit,
            Appropriations,
            FamilyOverview
        },
        
        data: function() {
            return {
                edit_mode: false
            }
        },
        computed: {
            cas: function() {
                return this.$store.getters.getCase
            },
            user: function() {
                return this.$store.getters.getUser
            }
        },
        watch: {
            cas: function() {
                if (this.cas.case_worker === this.user.id) {
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
                } else {
                    this.$store.commit('setBreadcrumb', [
                        {
                            link: '/all-cases',
                            title: 'Alle sager'
                        },
                        {
                            link: false,
                            title: `${ this.cas.sbsys_id}, ${ this.cas.name}`
                        }
                    ])
                }
            }
        },
        methods: {
            update: function() {
                this.$store.dispatch('fetchCase', this.$route.params.id)
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
            },
            displayEffortName: function(str) {
                return displayEffort(str)
            },
            displayUserName: function(id) {
                return userId2name(id)
            },
            displayTeamName: function(id) {
                return teamId2name(id)
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

    .case .actions {
        margin: 1rem;
    }

    .case .actions > * {
        margin: 0 .5rem;
    }
    
    .case-header .material-icons {
        font-size: 3rem;
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
