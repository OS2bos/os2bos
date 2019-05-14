<template>

    <nav class="breadcrumb" v-if="bc.length > 0">
        <span v-for="b in bc" :key="b[0]" class="crumb">
            <router-link :to="b.link" v-if="b.link">
                {{ b.title }}
            </router-link>
            <span v-if="!b.link">
                {{ b.title }}
            </span>
        </span>
    </nav>

</template>

<script>

    export default {

        computed: {
            bc: function() {
                return this.$store.getters.getBreadcrumb
            }
        }
        
    }
    
</script>

<style>

    .breadcrumb {
        padding: .25rem 1rem;
        border-bottom: solid 1px var(--grey1);
    }

    .breadcrumb .crumb {
        display: inline-block;
        padding: .25rem 0;
    }

    .breadcrumb .crumb::before {
        content: '>';
        display: inline-block;
        margin: 0 .5rem;
        opacity: .5;
    }

    .breadcrumb .crumb:first-child:before {
        content: '';
        margin: 0;
    }

    .breadcrumb .crumb > a  {
        border: none;
    }

</style>
