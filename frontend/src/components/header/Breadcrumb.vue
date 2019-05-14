<template>

    <nav class="breadcrumb" v-if="bc.length > 0">
        <span v-for="b in bc" :key="b[0]" class="crumb">
            <router-link :to="b.link">
                {{ b.title }}
            </router-link>
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
        font-size: 0.85em;
        padding: .25rem .5rem;
        border-bottom: solid 1px var(--grey1);
    }

    .breadcrumb .crumb {
        display: inline-block;
    }

    .breadcrumb .crumb::before {
        content: '>';
        display: inline-block;
        margin: .5rem;
        opacity: .5;
    }

</style>
