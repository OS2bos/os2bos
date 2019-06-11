<template>
    <div class="assessment" v-if="cas">
        <header class="assessment-header">
            <h1>Vurderinger af {{ cas.cpr_number }}, {{ cas.name }}</h1>
        </header>

        <form class="assessment-form" @submit.prevent="saveAssessment()">
            <assessment-edit :case-obj="cas" @assessment="updateAssessment" />
            <fieldset style="margin: 0 1rem 1rem;">
                <input type="submit" value="Opdatér">
            </fieldset>
        </form>

        <assessment-history :case-obj="cas" />
    </div>

</template>

<script>

    import AssessmentEdit from './AssessmentEdit.vue'
    import AssessmentHistory from './AssessmentHistory.vue'
    import axios from '../http/Http.js'

    export default {

        components: {
            AssessmentHistory,
            AssessmentEdit
        },

        data: function() {
            return {
                cas_id: null,
                cas: null
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
                .catch(err => console.log(err))
            },
            updateAssessment: function(assessment) {
                if (assessment.scaling_step) {
                    this.cas.scaling_step = assessment.scaling_step
                }
                if (assessment.effort_step) {
                    this.cas.effort_step = assessment.effort_step
                }
            },
            saveAssessment: function() {
                axios.patch(`/cases/${ this.cas_id}/`, {
                    scaling_step: this.cas.scaling_step,
                    effort_step: this.cas.effort_step
                })
                .then(res => {
                    this.update()
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

    .assessment-form {
        margin-bottom: 2rem;
    }

</style>