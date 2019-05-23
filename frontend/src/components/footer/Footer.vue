<template>

    <footer class="globalfooter">
        
        <button @click="submitTestData()">Opfind data (kun test)</button>

    </footer>

</template>

<script>

    import axios from '../http/Http.js'
    
    export default {

        methods: {
            submitTestData: function() {

                axios.post('/cases/', {
                    "user_created": "leil",
                    "sbsys_id": "46.46.24-64-ghis-872",
                    "cpr_number": "000000-0000",
                    "name": "Ejvind-Emil Hansen Persdatter",
                    "case_worker": "Inger Støjberg",
                    "target_group": "FAMILY_DEPT",
                    "refugee_integration": true,
                    "cross_department_measure": true,
                    "district": "1",
                    "paying_municipality": "1",
                    "acting_municipality": "1",
                    "residence_municipality": "1"
                })
                .then(res => {
                    console.log('posting went well')   
                })
                .catch(err => {
                    console.log('posting was a failure')   
                })
                axios.post('/cases/', {
                    "user_created": "Inger Støjberg",
                    "sbsys_id": "63.14.75-17-XHhi-4",
                    "cpr_number": "000000-0000",
                    "name": "Mona Smith",
                    "case_worker": "Inger Støjberg",
                    "target_group": "DISABILITY_DEPT",
                    "refugee_integration": false,
                    "cross_department_measure": false,
                    "district": "2",
                    "paying_municipality": "2",
                    "acting_municipality": "1",
                    "residence_municipality": "1"
                })
                .then(res => {
                    console.log('posting went well')   
                })
                .catch(err => {
                    console.log('posting was a failure')   
                })
                axios.post('/cases/', {
                    "user_created": "leil",
                    "sbsys_id": "56.17.45-10-bnih-84",
                    "cpr_number": "000000-0000",
                    "name": "Génevieve Macron",
                    "case_worker": "Leif L Lodahl",
                    "target_group": "FAMILY_DEPT",
                    "refugee_integration": false,
                    "cross_department_measure": false,
                    "district": "2",
                    "paying_municipality": "1",
                    "acting_municipality": "1",
                    "residence_municipality": "1"
                })
                .then(res => {
                    console.log('posting went well')   
                })
                .catch(err => {
                    console.log('posting was a failure')   
                })

            }
        }

    }

</script>

<style>

    .globalfooter {
        padding: 1rem;
        background-color: var(--grey1);
    }    

</style>
