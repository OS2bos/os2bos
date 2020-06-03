// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { login } from '../utils/logins.js'
import baseurl from '../utils/url.js'
import { leadZero, randNum, createDate } from '../utils/utils.js'
import { createCase, createAppropriation, createActivity, approveActivities } from '../utils/crud.js'

const today = new Date(),
    anotherday = new Date(new Date().setDate(today.getDate() + 2)),
    testdata = {
        case1: {
            name: `${ randNum() }.${ randNum() }.${ randNum() }-regel-test`
        },
        case2: {
            name: `${ randNum() }.${ randNum() }.${ randNum() }-regel-test`
        },
        appr1: {
            name: `${ randNum() }.${ randNum() }.${ randNum() }-regel-test-bevilling`
        },
        appr2: {
            name: `${ randNum() }.${ randNum() }.${ randNum() }-regel-test-bevilling`
        },
        act1: {
            start_today: `${ today.getFullYear() }-${ leadZero(today.getMonth() + 1) }-${ leadZero(today.getDate()) }`,
            end_date: `${ anotherday.getFullYear() }-${ leadZero(anotherday.getMonth() + 1) }-${ leadZero(anotherday.getDate()) }`
        },
        act2: {
            type: 1,
            start: createDate(3),
            amount: '12',
            payee_id: '89837837728',
            payee_name: 'Fiktiv Virksomhed I/S'
        },
        act3: {
            expected_type: 'adjustment',
            type: 1,
            start: createDate(5),
            amount: '15'
        }

    }

fixture `Check payments start date`
    .page(baseurl)
    .beforeEach(async t => { 
        await login(t) 
    })

test('Start date rule check for activities with "CASH" payment', async t => {

    await createCase(t, testdata.case1)
    await createAppropriation(t, testdata.appr1)

    await t
        .click(Selector('.activities-create-btn'))
        .click('#fieldSelectAct')
        .click(Selector('#fieldSelectAct option').nth(1))
        .typeText('#pay-date-start', testdata.act1.start_today)
        .click(Selector('label').withAttribute('for', 'pay-receiver-type-person'))
        .click(Selector('label').withAttribute('for', 'pay-method-cash'))
        .expect(Selector('.warning').exists).ok()
        .typeText('#pay-date-start', testdata.act1.end_date)
        .expect(Selector('.warning').exists).notOk()
})

test('Check that an activity may only have one modifier', async t => {

    await createCase(t, testdata.case2)
    await createAppropriation(t, testdata.appr2)
    await createActivity(t, testdata.act2)
    await approveActivities(t)
    
    await t.click(Selector('.act-list-item a'))

    await createActivity(t, testdata.act3)

    await t
        .click(Selector('.meta-row'))
        .click(Selector('.sub-row a'))
        .expect(Selector('button').withText('Lav forventet justering').exists).notOk()

})