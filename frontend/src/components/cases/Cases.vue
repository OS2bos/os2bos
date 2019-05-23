<template>

    <section class="cases" v-if="cas">
        <header class="cases-header">
            <h1>Mine sager</h1>
            <button class="create" @click="$router.push('case-create')">+ Tilknyt hovedsag</button>
        </header>
        <table>
            <thead>
                <tr>
                    <th>
                        SBSYS-hovedsag
                    </th> 
                    <th>
                        Borger
                    </th>
                    <th>
                        Ændret
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="c in cas" :key="c.id">
                    <td>
                        <i class="material-icons">folder_shared</i>
                        <router-link :to="`/case/${ c.id }`">
                            {{ c.sbsys_id }}
                        </router-link>
                    </td>
                    <td>
                        {{ c.cpr_number }} - {{ c.name }}
                    </td>
                    <td>
                        {{ displayDate(c.modified) }}
                    </td>
                </tr>
            </tbody>
        </table>
    </section>

</template>

<script>

    import axios from '../http/Http.js'
    import { json2js } from '../filters/Date.js'

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
                axios.get('/cases/')
                .then(res => {
                    this.cas = res.data
                })
                .catch(err => console.log(err))
            },
            displayDate: function(dt) {
                return json2js(dt)
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
