<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>
    <div class="assessment_history" v-if="cas">
        <header class="assessment-header">
            <h1>Vurderinger af {{ cas.cpr_number }}, {{ cas.name }}</h1>
        </header>

        <assessment-history :case-obj="cas" />
    </div>

</template>

<script>

    import AssessmentHistory from './AssessmentHistory.vue'
    import axios from '../http/Http.js'

    export default {

        components: {
            AssessmentHistory
        },

        data: function() {
            return {
                cas_id: null,
                cas: null,
                disableButton: true
            }
        },
        methods: {
            update: function() {
                this.cas_id = this.$route.params.id
                this.fetchCase(this.cas_id)
            },
            fetchCase: function(id) {
                axios.get(`/cases/${ this.cas_id}/`)
                .then(res => {
                    this.cas = res.data
                    this.$store.commit('setBreadcrumb', [
                        {
                            link: '/',
                            title: 'Mine sager'
                        },
                        {
                            link: `/case/${ this.cas.id }/`,
                            title: `Sag ${ this.cas.sbsys_id }`
                        },
                        {
                            title: `Vurderinger`
                        }
                    ])
                })
                .catch(err => console.error(err))
            },
        },
        created: function() {
            this.update()
        }
    }
    
</script>

<style>

    .assessment_history {
        margin: 1rem;
    }

    .assessment-form {
        margin-bottom: 2rem;
    }

</style>