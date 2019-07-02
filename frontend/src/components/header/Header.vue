<template>

    <header>
        <div class="globalheader">
            <h1 title="Ballerup Bevillingsplatformen">
                <router-link to="/" class="header-link">
                    <img class="global-logo" src="/logo.png" alt="" />
                    <span class="global-brandname">Bevillingsplatformen</span>
                </router-link>
            </h1>
            <user-actions />
        </div>
        <breadcrumb />
    </header> 

</template>

<script>

    import Breadcrumb from './Breadcrumb.vue'
    import UserActions from '../auth/UserActions.vue'
    
    export default {

        components: {
            Breadcrumb,
            UserActions
        }

    }

</script>

<style>

    .globalheader {
        display: flex;
        flex-flow: row nowrap;
        justify-content: space-between;
        align-items: center;
        padding: 2rem;
        background-color: var(--grey0);
    }

    .globalheader > h1 {
        margin: 0;
        padding: 0;
        display: block;
    }

    .header-link {
        display: block;
        margin: 0;
        padding: 0;
        border: none !important;
        position: relative;
    }

    .global-logo {
        height: 3.5rem;
        width: auto;
        opacity: 1;
        margin: 0 .5rem 0 0;
    }

    .global-brandname {
        position: absolute;
        bottom: 0.25rem;
        left: 3.375rem;
        font-size: 1rem;
        letter-spacing: 1px;
        color: var(--grey10);
        text-transform: uppercase;
    }

</style>
