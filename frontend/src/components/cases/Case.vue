<template>

    <section v-if="cas">
        <h1 class="case">Sag {{ cas[0].sbsys_id }}</h1>
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
                    this.cas = res.data
                    this.$store.commit('setBreadcrumb', [
                        {
                            link: '/',
                            title: 'Mine sager'
                        },
                        {
                            link: false,
                            title: `Sag ${ this.cas[0].sbsys_id}`
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
