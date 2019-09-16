<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <section class="case" v-if="cas">

        <header class="case-header">
            <h1 style="padding: 0;">
                <i class="material-icons">folder_shared</i>
                Hovedsag {{ cas.sbsys_id }}
            </h1>
            <div v-if="!edit_mode" class="actions">
                <button @click="edit_mode = !edit_mode">Redigér</button>
            </div>
        </header>

        <case-edit :case-obj="cas" v-if="edit_mode" @close="reload()" />

        <div class="row" v-if="!edit_mode">
            <div class="case-info case-info-grid row-item">
                <dl>
                    <dt>Sagspart (CPR, navn)</dt>
                    <dd>
                        {{ cas.cpr_number }}, {{ cas.name }}
                    </dd>
                
                    <dt>Indsatstrappen</dt>
                    <dd>{{ displayEffortName(cas.effort_step) }}</dd>
                
                    <dt>Skaleringstrappe</dt>
                    <dd>
                        {{ cas.scaling_step }}
                        <router-link :to="`/case/${ cas.id }/assessment`" style="margin-left: 1rem;">Se vurderinger</router-link>
                    </dd>

                    <template v-if="cas.note">
                        <dt>Supplerende oplysninger</dt>
                        <dd>{{ cas.note }}</dd>
                    </template>
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
            
            <family-overview :case-id="cas.id" class="row-item" />
            
        </div>

        <appropriations :case-id="cas.id" />

    </section>

</template>

<script>

    import CaseEdit from './CaseEdit.vue'
    import Appropriations from '../appropriations/AppropriationList.vue'
    import FamilyOverview from '../familyoverview/FamilyOverview.vue'
    import axios from '../http/Http.js'
    import { municipalityId2name, districtId2name, displayEffort, userId2name, teamId2name } from '../filters/Labels.js'
    import store from '../../store.js'

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
        beforeRouteEnter: function(to, from, next) {
            store.commit('clearCase')
            store.dispatch('fetchCase', to.params.caseId)
            .then(() => next())
        },
        beforeRouteUpdate: function(to, from, next) {
            store.dispatch('fetchCase', to.params.caseId)
            .then(() => next())
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
            reload: function() {
                this.edit_mode =  false
                this.$store.dispatch('fetchCase', this.$route.params.caseId)
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
        }
    }
    
</script>

<style>

    .case {
        margin: 1rem 2rem;
    }

    .case .case-header {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
    }

    .case .case-edit {
        margin: 1rem 0 2rem;
    }

    .case .row {
        align-items: stretch;
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

    .case-info-grid {
        align-content: flex-start;
        align-items: flex-start;
        background-color: var(--grey1);
        display: flex;
        flex-flow: row wrap;
        margin: 0 0 2rem;
        padding: 1.5rem 0 0;
    }

    .case-info-grid dl {
        margin: 0 2rem 2rem;
        flex: 0 1 auto;
    }

    .case .familyoverview {
        margin: 0 0 2rem;
        border: solid 1px var(--grey2);
        padding: 1rem 2rem;
    }

</style>
