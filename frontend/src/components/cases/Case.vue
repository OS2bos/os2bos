<template>

    <section v-if="cas">
        <h1 class="case">{{ cas.sbsys_id }}</h1>
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
                this.fetch_case(this.$route.params.id)
            },
            fetch_case: function(id) {
                axios.get('../../case.json')
                .then(res => {
                    this.cas = res.data
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
