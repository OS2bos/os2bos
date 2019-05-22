<template>

    <section class="cases" v-if="cas">
        <header class="cases-header">
            <h1>Mine sager</h1>
            <button class="create" @click="$router.push('case-create')">+ Tilføj SBSYS-reference</button>
        </header>
        <table>
            <thead>
                <tr>
                    <th>
                        SBSYS-reference
                    </th> 
                    <th>
                        Borger
                    </th>
                    <th>
                        CPR-nr
                    </th>
                    <th>
                        Ændret
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="c in cas" :key="c.pk">
                    <td>
                        <router-link :to="`/case/${ c.pk }`">
                            {{ c.sbsys_id }}
                        </router-link>
                    </td>
                    <td>
                        {{ c.name }}
                    </td>
                    <td>
                        {{ c.cpr_no }}
                    </td>
                    <td>
                        {{ c.updated }}
                    </td>
                </tr>
            </tbody>
        </table>
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

    .cases-header {
        display: flex;
        flex-flow: row nowrap;
        justify-content: space-between;
        align-items: center;
    }

    .create {
        margin-top: 1rem;
    }

</style>
