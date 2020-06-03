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
                <button v-if="permissionCheck === true" @click="edit_mode = !edit_mode">Redigér</button>
            </div>
        </header>

        <case-edit :case-obj="cas" v-if="edit_mode" @close="reload()" />

        <div class="case-info-main" v-if="!edit_mode">
            <div class="case-info case-info-grid">
                <dl>
                    <dt>Sagspart (CPR, navn)</dt>
                    <dd>
                        {{ cas.cpr_number }}, {{ cas.name }}
                    </dd>

                    <template v-if="cas.effort_step">
                        <dt>Indsatstrappen</dt>
                        <dd v-html="displayEffortName(cas.effort_step)"></dd>
                    </template>
                
                    <template v-if="cas.scaling_step">
                        <dt>Skaleringstrappe</dt>
                        <dd>
                            {{ cas.scaling_step }}<br>
                        </dd>
                    </template>

                    <template v-if="cas.effort_step || cas.scaling_step">
                        <dt>Vurderinger</dt>
                        <dd>
                            <router-link :to="`/case/${ cas.id }/assessment`" style="display: inline-block; margin-top: .5rem;">Se vurderinger</router-link>
                        </dd>
                    </template>

                    <template v-if="cas.note">
                        <dt>Supplerende oplysninger</dt>
                        <dd>{{ cas.note }}</dd>
                    </template>
                </dl>
                <dl>
                    <dt>Målgruppe</dt>
                    <dd v-html="displaytargetGroup(cas.target_group)"></dd>

                    <template v-if="cas.target_group">
                        <dt>Skoledistrikt</dt>
                        <dd v-html="displayDistrictName(cas.district)"></dd>
                    </template>

                    <div v-if="cas.efforts.length">
                        <dt>Indsatser</dt>
                        <template v-for="effort in cas.efforts">
                            <dd :key="effort.id" v-html="displayEffort(effort)"></dd>
                        </template>
                    </div>
                </dl>
                <dl>
                    <dt>Sagsbehandler</dt>
                    <dd>{{ displayUserName(cas.case_worker) }}</dd>
                
                    <dt>Team</dt>
                    <dd>{{ displayTeamName(cas.team).name }}</dd>
                
                    <dt>Leder</dt>
                    <dd>{{ displayUserName( displayTeamName(cas.team).leader ) }}</dd>
                </dl>
                <dl>
                    <dt>Betalingskommune</dt>
                    <dd v-html="displayMuniName(cas.paying_municipality)"></dd>
                
                    <dt>Handlekommune</dt>
                    <dd v-html="displayMuniName(cas.acting_municipality)"></dd>
                
                    <dt>Bopælsskommune</dt>
                    <dd v-html="displayMuniName(cas.residence_municipality)"></dd>

                </dl>

            </div>

            <family-overview :case-id="cas.id" />
            
        </div>

        <appropriations :case-id="cas.id" />

    </section>

</template>

<script>

    import CaseEdit from './CaseEdit.vue'
    import Appropriations from '../appropriations/AppropriationList.vue'
    import FamilyOverview from '../familyoverview/FamilyOverview.vue'
    import axios from '../http/Http.js'
    import { municipalityId2name, targetGroupId2name, districtId2name, effortId2name, displayEffort, userId2name, teamId2name } from '../filters/Labels.js'
    import store from '../../store.js'
    import UserRights from '../mixins/UserRights.js'

    export default {

        mixins: [UserRights],

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
                this.$store.commit('setBreadcrumb', [
                    {
                        link: '/',
                        title: 'Sager'
                    },
                    {
                        link: false,
                        title: `${ this.cas.sbsys_id}, ${ this.cas.name}`
                    }
                ])
            },
            user: function() {
                this.reload()
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
            displaytargetGroup: function(id) {
                return targetGroupId2name(id)
            },
            displayEffort: function(id) {
                return effortId2name(id)
            },
            displayEffortName: function(id) {
                return displayEffort(id)
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

    .case-info-main {
        background-color: var(--grey1);
        padding: 1.5rem 2rem 2rem;
        display: grid;
        grid-template-columns: 1fr 1fr;
        margin-bottom: 2.5rem;
    }

    .case-info-grid {
        height: auto;
        display: grid;
        grid-template-columns: repeat( auto-fit, minmax(15rem, 1fr) );
        grid-template-rows: max-content max-content;
        gap: 2rem;
    }

    .case-info-grid dl {
        border-right: solid 1px var(--grey0);
        padding-right: 2rem;
    }

    .case .familyoverview {
        margin: 0 0 0 2rem;
        padding: 0;
    }

</style>
