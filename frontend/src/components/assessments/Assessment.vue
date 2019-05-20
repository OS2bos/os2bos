<template>
    <section class="assessment">
        <header class="assessment-header">
            <h1>Vurderinger</h1>
            <button v-if="!show_edit" @click="show_edit = true" class="assessment-edit-btn">Redigér</button>
        </header>
        <div>
            <fieldset v-if="!show_edit">
                <h3>Sagspart:</h3>
                <dl>
                    <dt>CPR-nr:</dt>
                    <dd>{{ cas.cpr_no }}</dd>
                    <dt>Navn:</dt>
                    <dd>{{ cas.name }}</dd>
                    <dt>Sag:</dt>
                    <dd>{{ cas.sbsys_id }}</dd>
                </dl>
            </fieldset>

             <div v-if="show_edit">
                <assessment-edit :assessment-data="cas" @cancelled="show_edit = false" @saved="show_edit = false" />
            </div>

            <history/>
        </div>
    </section>

</template>

<script>

    import AssessmentEdit from './AssessmentEdit.vue'
    import History from './History.vue'
    import axios from '../http/Http.js'

    export default {

        components: {
            History,
            AssessmentEdit
        },

        data: function() {
            return {
                cas: null,
                show_edit: false
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
                            title: `Sag ${ this.cas.sbsys_id }`
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

    .assessment-header {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
        justify-content: flex-start;
    }

    .assessment .assessment-edit-btn {
        margin: 0 1rem;
    }

</style>