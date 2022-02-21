import { ClientFunction } from 'testcafe'
import { familieleder } from '../utils/logins.js'
import baseurl from '../utils/url.js'
import checkConsole from '../utils/console.js'
import { navToActivity } from '../utils/navigation.js'
import * as testdata from '../testdata.js'

const postAJAX = ClientFunction(payload => {
    
    return fetch(payload.url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json;charset=utf-8'
        },
        body: JSON.stringify(payload.data)
    })
    .then(response => response.json())
    .then(json_res => json_res)
    .catch(err => `ERROR: ${err}`)
})

const patchAJAX = ClientFunction(payload => {
    
    return fetch(payload.url, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json;charset=utf-8'
        },
        body: JSON.stringify(payload.data)
    })
    .then(response => response.json())
    .then(json_res => json_res)
    .catch(err => `ERROR: ${err}`)
})

fixture('Create data')
    .beforeEach(async t => { 
        await t.useRole(familieleder)
    })
    .page(baseurl)
    .afterEach(() => checkConsole())

test('Initialize some data', async t => {

    const responses = await Promise.all([
        postAJAX({url: `${baseurl}/api/cases/`, data: testdata.case1}),
        postAJAX({url: `${baseurl}/api/cases/`, data: testdata.case2}),
        postAJAX({url: `${baseurl}/api/cases/`, data: testdata.case3}),
        postAJAX({url: `${baseurl}/api/cases/`, data: testdata.case4}),
        postAJAX({url: `${baseurl}/api/cases/`, data: testdata.case5}),
        postAJAX({url: `${baseurl}/api/cases/`, data: testdata.case6}),
        postAJAX({url: `${baseurl}/api/cases/`, data: testdata.case7}),
        postAJAX({url: `${baseurl}/api/cases/`, data: testdata.case81}),
        postAJAX({url: `${baseurl}/api/cases/`, data: testdata.case82})
    ])

    // Because REST API automatically sets `case_worker` to the currently logged in user, 
    // we need to manually patch cases that should have another `case_worker`
    await Promise.all([
        patchAJAX({url: `${baseurl}/api/cases/${responses[6].id}/`, data: {case_worker: 3}}),
        patchAJAX({url: `${baseurl}/api/cases/${responses[7].id}/`, data: {case_worker: 2}}),
        patchAJAX({url: `${baseurl}/api/cases/${responses[8].id}/`, data: {case_worker: 3}})
    ])

    testdata.appr21.case = responses[0].id
    testdata.appr22.case = responses[1].id
    testdata.appr3.case = responses[2].id
    testdata.appr4.case = responses[3].id
    testdata.appr5.case = responses[4].id
    testdata.appr7.case = responses[6].id
    testdata.appr81.case = responses[7].id
    testdata.appr82.case = responses[8].id
    testdata.appr83.case = responses[8].id

    const appr_responses = await Promise.all([
        postAJAX({url: `${baseurl}/api/appropriations/`, data: testdata.appr21}),
        postAJAX({url: `${baseurl}/api/appropriations/`, data: testdata.appr22}),
        postAJAX({url: `${baseurl}/api/appropriations/`, data: testdata.appr3}),
        postAJAX({url: `${baseurl}/api/appropriations/`, data: testdata.appr4}),
        postAJAX({url: `${baseurl}/api/appropriations/`, data: testdata.appr5}),
        postAJAX({url: `${baseurl}/api/appropriations/`, data: testdata.appr7}),
        postAJAX({url: `${baseurl}/api/appropriations/`, data: testdata.appr81}),
        postAJAX({url: `${baseurl}/api/appropriations/`, data: testdata.appr82}),
        postAJAX({url: `${baseurl}/api/appropriations/`, data: testdata.appr83})
    ])

    testdata.appr21.id = appr_responses[0].id
    testdata.appr22.id = appr_responses[1].id
    testdata.appr3.id = appr_responses[2].id
    testdata.appr4.id = appr_responses[3].id
    testdata.appr5.id = appr_responses[4].id
    testdata.appr7.id = appr_responses[5].id
    testdata.appr81.id = appr_responses[6].id
    testdata.appr82.id = appr_responses[7].id
    testdata.appr83.id = appr_responses[8].id

    testdata.act71.appropriation = appr_responses[5].id
    testdata.act72.appropriation = appr_responses[5].id
    testdata.act73.appropriation = appr_responses[5].id
    testdata.act74.appropriation = appr_responses[5].id

    const act_responses = await Promise.all([
        postAJAX({url: `${baseurl}/api/activities/`, data: testdata.act71}),
        postAJAX({url: `${baseurl}/api/activities/`, data: testdata.act72}),
        postAJAX({url: `${baseurl}/api/activities/`, data: testdata.act73}),
        postAJAX({url: `${baseurl}/api/activities/`, data: testdata.act74})
    ])

    testdata.act71.id = act_responses[0].id
    testdata.act72.id = act_responses[1].id
    testdata.act73.id = act_responses[2].id
    testdata.act74.id = act_responses[3].id

    // Sample check to see if any data was created
    await navToActivity(t, testdata.act74.id)

})
