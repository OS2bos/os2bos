<template>

    <section class="case" v-if="cas">
        <h1>
            <i class="material-icons">folder_shared</i>
            Hovedsag {{ cas.sbsys_id }}
        </h1>
        <dl>
            <dt>Sagspart (CPR, navn)</dt>
            <dd>{{ cas.cpr_number }}, {{ cas.name }}</dd>
            <dt>Betalingskommune:</dt>
            <dd>{{ cas.paying_municipality }}</dd>
            <dt>Handlekommune:</dt>
            <dd>{{ cas.acting_municipality }}</dd>
            <dt>Bopælsskommune:</dt>
            <dd>{{ cas.residence_municipality }}</dd>
            <dt>Indsatstrappen:</dt>
            <dd>{{ cas.effort_stairs }}</dd>
            <dt>Skaleringstrappe:</dt>
            <dd>{{ cas.scaling_staircase }}</dd>
            <dt>Sagsbehander:</dt>
            <dd>{{ cas.case_worker }}</dd>
            <dt>Team:</dt>
            <dd>ikke implementeret</dd>
            <dt>Distrikt:</dt>
            <dd>{{ cas.district}}</dd>
            <dt>Leder:</dt>
            <dd>ikke implementeret</dd>
        </dl>
        <appropriations />
    </section>

</template>

<script>

    import Appropriations from '../appropriations/AppropriationList.vue'
    import axios from '../http/Http.js'

    export default {

        components: {
            Appropriations
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

</style>
