<template>

    <section class="case" v-if="cas">
        <h1>
            <i class="material-icons">folder_shared</i>
            Hovedsag {{ cas.sbsys_id }}
        </h1>
        <dl>
            <dt>Sagspart (CPR, navn)</dt>
            <dd>{{ cas.cpr_no }}, {{ cas.name }}</dd>
            <dt>Betalingskommune:</dt>
            <dd>{{ cas.municipality.payment_municipality}}</dd>
            <dt>Handlekommune:</dt>
            <dd>{{ cas.municipality.payment_municipality}}</dd>
            <dt>Bopælsskommune:</dt>
            <dd>{{ cas.municipality.payment_municipality}}</dd>
            <dt>Indsatstrappen:</dt>
            <dd>{{ cas.effort_stairs }}</dd>
            <dt>Skaleringstrappe:</dt>
            <dd>{{ cas.scaling_staircase }}</dd>
            <dt>Sagsbehander:</dt>
            <dd>{{ cas.case_management.case_worker }}</dd>
            <dt>Team:</dt>
            <dd>{{ cas.case_management.team }}</dd>
            <dt>Distrikt:</dt>
            <dd>{{ cas.original_district}}</dd>
            <dt>Leder:</dt>
            <dd>{{ cas.case_management.manager }}</dd>
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
                axios.get('../../case-data.json')
                .then(res => {
                    this.cas = res.data[0]
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
