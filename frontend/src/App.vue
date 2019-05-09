<template>
    <div id="app">
        <header>

        </header>
        <main>
            <router-view/>
        </main>
        <footer>

        </footer>
    </div>
</template>

<style>

    .list {
        list-style: none;
        padding: 0;
        margin: 0;   
    }

    .list > li {
        padding: .5rem;
        border-top: solid 1px hsla(0,0%,0%,.25);
    }

</style>
