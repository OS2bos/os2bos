<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->


<template>

    <div class="useractions" v-if="auth">
        <p style="margin: 0 1rem;">
            <strong>
                {{ user.fullname }}
            </strong>
            <br>
            {{ team.name }}
        </p>
    </div>

</template>

<script>
export default {
    computed: {
        auth: function() {
            return this.$store.getters.getAuth
        },
        user: function() {
            return this.$store.getters.getUser
        },
        team: function() {
            return this.$store.getters.getTeam
        }
    }
}
</script>

<style>

    .useractions {
        display: flex;
        flex-flow: row nowrap;
        align-items: center;
    }
</style>