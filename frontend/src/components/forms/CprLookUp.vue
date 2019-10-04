<!-- Copyright (C) 2019 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>

    <div class="cpr-lookup">

        <label class="required" for="field-cpr">CPR-nr</label>
        <input 
            id="field-cpr" 
            type="text" 
            v-model="instance_cpr" 
            @input="lookupCPR(instance_cpr)"
            maxlength="11" minlength="10"
            pattern="[0-9-]{10,11}"
            title="Det indtastede skal være et gyldigt personnummer"
            required>
        <error err-key="cpr_number" />
        
        <label class="required" for="field-name">Navn</label>
        <input 
            id="field-name"
            type="text"
            v-model="instance_name"
            @input="$emit('update:name', instance_name)"
            required>
        <error err-key="name" />
        
    </div>

</template>

<script>

    import axios from '../http/Http.js'
    import Error from '../forms/Error.vue'
    import notify from '../notifications/Notify';

    export default {

        components: {
            Error
        },
        props: [
            'cpr',
            'name'
        ],
        data: function() {
            return {
                instance_cpr: null,
                instance_name: null
            }
        },
        watch: {
            cpr: function() {
                this.update()
            },
            name: function() {
                this.update()
            }
        },
        methods: {
            update: function() {
                if (this.cpr) {
                    this.instance_cpr = this.cpr    
                }
                if (this.name) {
                    this.instance_name = this.name
                }
            },
            lookupCPR: function(cpr_no) {
                const cpr = cpr_no.replace('-','')
                if (cpr.length > 9) {
                    axios.get(`/related_persons/fetch_from_serviceplatformen/?cpr=${ cpr }`)
                    .then(res => {
                        this.instance_name = res.data.name
                        this.$emit('update:cpr', cpr)
                        this.$emit('update:name', res.data.name)
                        this.$emit('update:relations', res.data.relations)
                    })
                    .catch(err => {
                        this.$emit('update:cpr', cpr)
                        notify('Der skete en fejl ved opslag af CPR', 'error')
                        this.$store.dispatch('parseErrorOutput', err)
                    })
                }  
            }
        },
        created: function() {
            this.update()
        }

    }

</script>
