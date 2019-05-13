<template>

    <section class="cases" v-if="cas">
        <h1>Mine sager</h1>
        <table>
            <tr>
                <td>
                    Sags-ID
                </td> 
                <td>
                    Navn
                </td>
                <td>
                    Status
                </td>
                <td>
                    Ændret
                </td>
            </tr>
            <tr v-for="c in cas" :key="c[0]">
                <td>
                    <router-link :to="`/case/${ c.pk }`">
                        {{ c.sbsys_id }}
                    </router-link>
                </td>
                <td>
                    {{ c.name }}
                </td>
                <td>
                    -
                </td>
                <td>
                    {{ c.updated }}
                </td>
            </tr>
        </table>

        <button class="create" @click="$router.push('case-create')">Opret sag</button>
    </section>

</template>

<script>

    import axios from '../http/Http.js'

    export default {

        data: function() {
            return {
                cas: null
            }
        },
        methods: {
            update: function() {
                this.fetchCases(this.$route.params.id)
            },
            fetchCases: function(id) {
                axios.get('../../case-data.json')
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

    .cases {
        margin: 1rem;
    }
    .create {
        margin-top: 1rem;
    }

</style>
