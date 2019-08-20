<template>

    <div class="danger error" v-if="msgs">
        <p v-for="m in msgs" :key="m[0]">
            {{ m }}
        </p>
    </div>

</template>

<script>

    import notify from '../notifications/Notify.js'

    export default {

        props: [
            'msgs'
        ],
        methods: {
            handleError: function(error) {
                let msgs = {error: ['Der skete en fejl']}
                if (error.response) {
                    msgs = error.response.data // return the error JSON object
                    for (let m in msgs) {
                        notify(msgs[m][0], 'error')
                    }
                } else if (error.request) {
                    msgs = {error: [error.request.responseText]}
                    notify(msgs.error[0], 'error')
                } else if (error.message) {
                    msgs = {error: [error.message]}
                    notify(msgs.error[0], 'error')
                }
                return msgs
            }
        }

    }

</script>

<style>

    .error span {
        text-transform: capitalize;
    }

</style>