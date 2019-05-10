<template>

    <section class="appropriation" v-if="appr">
        <router-link to="/case/1">Sag XXX</router-link>
        <h1>Bevillingsskrivelse {{ appr.sbsys_id }}</h1>
        <dl>
            <dt>Paragraf</dt>
            <dd>{{ appr.law_ref }}</dd>
            <dt>Status</dt>
            <dd><span :class="`status-${ appr.status }`">{{ appr.status }}</span></dd>
            <template v-if="appr.approval">
                <dt>Bevilget af</dt>
                <dd>
                    {{ appr.approval.approval_person }}, 
                    {{ appr.approval.approval_auth_level }} 
                    - {{ new Date(appr.approval.approval_date).toLocaleDateString() }}
                </dd>
            </template>
        </dl>
        <activity-list :appr-id="appr.pk" />
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import ActivityList from '../activities/ActivityList.vue'

    export default {

        components: {
            ActivityList
        },
        data: function() {
            return {
                appr: null
            }
        },
        methods: {
            update: function() {
                this.fetch_appr(this.$route.params.id)
            },
            fetch_appr: function(id) {
                axios
                .get('../../appropriation-data.json')
                .then(res => {
                    this.appr = res.data
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

    .appropriation {
        margin: 1rem;
    }

    .appropriation .status-bevilget {
        background-color: green;
        color: white;
        padding: .25rem;
    }

</style>
