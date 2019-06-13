const axios = require('axios');

function postSuccess(res) {
    console.log('posting went well')
}

function postFail(err) {
    console.log('posting was a failure')
    console.log(err.response.data)   
}

function authLogin() {

    //Auth Login
    return axios.post('http://localhost:8000/api/token/', {
        "username": "sagsbehandler",
        "password": "sagsbehandler"
    })
    .then(res => {
        postSuccess(res)
        axios.defaults.headers.common['Authorization'] = `Bearer ${ res.data.access }`
    })
    .catch(err => { postFail(err) })
}

function testData() {

    // Create cases
    axios.post('http://localhost:8000/api/cases/', {
        "user_created": "leil",
        "sbsys_id": "46.46.24-64-ghis-872",
        "cpr_number": "000000-0000",
        "name": "Ejvind-Emil Hansen Persdatter",
        "case_worker": "1",
        "target_group": "FAMILY_DEPT",
        "refugee_integration": true,
        "cross_department_measure": true,
        "district": "1",
        "paying_municipality": "42",
        "acting_municipality": "42",
        "residence_municipality": "42",
        "scaling_step": 1,
        "effort_step": "STEP_ONE"
    })
    .then(res => { 

        postSuccess(res) 
        axios.post('http://localhost:8000/api/appropriations/', {
            "sbsys_id": "77.25.25-72-nhis-0184",
            "section": 12,
            "status": "DRAFT",
            "case": res.data.id
        })
        .then(res => { postSuccess(res) })
        .catch(err => { postFail(err) })
        axios.post('http://localhost:8000/api/appropriations/', {
            "sbsys_id": "34.34.95-15-xoiu-1",
            "section": 12,
            "status": "DRAFT",
            "case": res.data.id
        })
        .then(res => { postSuccess(res) })
        .catch(err => { postFail(err) })
        axios.post('http://localhost:8000/api/appropriations/', {
            "sbsys_id": "89.89.72-1-abie-082",
            "section": 62,
            "status": "DRAFT",
            "case": res.data.id
        })
        .then(res => { postSuccess(res) })
        .catch(err => { postFail(err) })

    })
    .catch(err => { postFail(err) })
    axios.post('http://localhost:8000/api/cases/', {
        "user_created": "Inger Støjberg",
        "sbsys_id": "63.14.75-17-XHhi-4",
        "cpr_number": "000000-0000",
        "name": "Mona Smith",
        "case_worker": "1",
        "target_group": "DISABILITY_DEPT",
        "refugee_integration": false,
        "cross_department_measure": false,
        "district": "2",
        "paying_municipality": 42,
        "acting_municipality": 42,
        "residence_municipality": 42,
        "scaling_step": 2,
        "effort_step": "STEP_TWO"
    })
    .then(res => { 

        postSuccess(res) 
        axios.post('http://localhost:8000/api/appropriations/', {
            "sbsys_id": "71.95.10-00-qygs-1",
            "section": 15,
            "status": "DRAFT",
            "case": res.data.id
        })
        .then(res => { postSuccess(res) })
        .catch(err => { postFail(err) })
        axios.post('http://localhost:8000/api/appropriations/', {
            "sbsys_id": "85.82.12-2-xniw-28",
            "section": 23,
            "status": "DRAFT",
            "case": res.data.id
        })
        .then(res => { postSuccess(res) })
        .catch(err => { postFail(err) })

    })
    .catch(err => { postFail(err) })
    axios.post('http://localhost:8000/api/cases/', {
        "user_created": "leil",
        "sbsys_id": "56.17.45-10-bnih-84",
        "cpr_number": "000000-0000",
        "name": "Génevieve Macron",
        "case_worker": "1",
        "target_group": "FAMILY_DEPT",
        "refugee_integration": false,
        "cross_department_measure": false,
        "district": "2",
        "paying_municipality": "42",
        "acting_municipality": "42",
        "residence_municipality": "42",
        "scaling_step": 3,
        "effort_step": "STEP_THREE"
    })
    .then(res => { 
        
        postSuccess(res) 
        axios.post('http://localhost:8000/api/appropriations/', {
            "sbsys_id": "98.08.23-17-lokq-26",
            "section": 6,
            "status": "DRAFT",
            "case": res.data.id
        })
        axios.post('http://localhost:8000/api/related_persons/', {
            "id": 1,
            "relation_type": "Mor",
            "cpr_number": "121290-1122",
            "name": "Camilla Yanez Macron",
            "related_case": "56.17.45-10-bnih-84",
            "main_case": 3
        })
        .then(apprres => { 
            postSuccess(apprres)
            axios.post('http://localhost:8000/api/activities/', {
                "id": 3,
                "revision": "",
                "created": "2019-05-28T12:50:14.362135+02:00",
                "modified": "2019-05-28T12:50:14.362135+02:00",
                "user_created": "Morten Krog Jensen",
                "user_modified": "Lilly Pardés",
                "hostname_created": "",
                "hostname_modified": "3569913b5d23",
                "device_created": "",
                "device_modified": "",
                "status": "EXPECTED",
                "start_date": "2019-05-28",
                "end_date": "2019-11-08",
                "activity_type": "MAIN_ACTIVITY",
                "service": 36,
                "payment_plan": null,
                "main_activity": null,
                "modifies": null,
                "appropriation": apprres.data.id
            })
            .then(resact => { postSuccess(resact) })
            .catch(err => { postFail(err) })

            axios.post('http://localhost:8000/api/activities/', {
                "id": 2,
                "revision": "",
                "created": "2019-05-28T16:15:29.257103+02:00",
                "modified": "2019-05-28T16:15:29.257103+02:00",
                "user_created": "Ole Skipper",
                "user_modified": "Mette Sørensen",
                "hostname_created": "",
                "hostname_modified": "635702a98058",
                "device_created": "",
                "device_modified": "",
                "status": "GRANTED",
                "start_date": "2019-05-27",
                "end_date": "2019-10-22",
                "activity_type": "MAIN_ACTIVITY",
                "service": 16,
                "payment_plan": null,
                "main_activity": null,
                "modifies": null,
                "appropriation": apprres.data.id
            })
            .then(resact => { postSuccess(resact) })
            .catch(err => { postFail(err) })
        
        })
        .catch(err => { postFail(err) })

    })
    .catch(err => { postFail(err) })

}

async function submitTestData() {
   await authLogin()
   testData()
}

submitTestData()