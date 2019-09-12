<template>

    <article id="browsercheck" v-if="warn_user">
        <h2>
            Din internet-browser er ikke opdateret
        </h2>
        <p>
            Din internet-browser er af ældre dato og den understøttes muligvis ikke af dette site.<br> 
            Nogle funktioner vil ikke fungere for dig.
        </p>
        <p>
            Vi anbefaler, at du opdaterer din browser eller bruger en nyere browser, <a href="https://www.mozilla.org/da/firefox/new/" title="Hent og installér Firefox">f.eks. Firefox.</a>
        </p>
        <p>
            <button @click="setGotIt()" id="accept">Jeg forstår</button>
        </p>
    </article>

</template>


<script>

    export default {
        data: function() {
            return {
                warn_user: false
            }
        },
        methods: {
            setGotIt: function() {
                localStorage.setItem('browser_is_old_409ce5ebdea1729cdf85ac4d9b55cdf4', 'understood')
                this.warn_user = false
            },
            checkBrowser: function() {
                if (!localStorage.getItem('browser_is_old_409ce5ebdea1729cdf85ac4d9b55cdf4')) {
                    const user_agent = navigator.userAgent,
                        regx = /MSIE|Trident/i
                    if (user_agent.search(regx) !== -1) {
                        this.warn_user = true
                    }
                }
            }
        },
        created: function() {
            this.checkBrowser()
        }
    }

</script>


<style>

    #browsercheck {
        position: fixed;
        top: 0;
        bottom: 0;
        left: 0;
        right: 0;
        width: 100%;
        height: 100%;
        overflow: auto;
        padding: 4rem 2rem;
        background-color: var(--grey1);
        z-index: 1000;
        display: flex;
        flex-flow: column nowrap;
        justify-content: flex-start;
        align-items: center;
    }

    #browsercheck > * {
            width: 100%;
            max-width: 60rem;
            margin: .5rem 1rem;
            flex: 0 1 auto;
    }
    

    @media screen and (min-width: 60rem) {

        #browsercheck {
            box-shadow: 0 -.5rem 0 hsla(0,0%,0%,.3);
            top: auto;
            height: auto;     
        }        

    }

</style>
