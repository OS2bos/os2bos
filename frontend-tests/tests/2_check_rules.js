// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { login } from '../utils/logins.js'
import baseurl from '../utils/url.js'
import { leadZero, randNum, createDate } from '../utils/utils.js'
import { createCase, createAppropriation, createActivity, approveActivities, editActivity } from '../utils/crud.js'

const today = new Date(),
    anotherday = new Date(new Date().setDate(today.getDate() + 7)),
    testdata = {
        case1: {
            name: `${ randNum() }.${ randNum() }.${ randNum() }-regel-test`,
            effort_step: '4',
            scaling_step: '4',
            target_group: 'Handicapafdelingen'
        },
        case2: {
            name: `${ randNum() }.${ randNum() }.${ randNum() }-regel-test`,
            effort_step: '2',
            scaling_step: '8',
            target_group: 'Familieafdelingen',
            district: 'Baltorp'
        },
        appr1: {
            name: `${ randNum() }.${ randNum() }.${ randNum() }-regel-test-bevilling`,
            section: 'SEL-109 Botilbud, kriseramte kvinder'
        },
        appr2: {
            name: `${ randNum() }.${ randNum() }.${ randNum() }-regel-test-bevilling`,
            section: 'SEL-109 Botilbud, kriseramte kvinder'
        },
        act1: {
            start_today: `${ today.getFullYear() }-${ leadZero(today.getMonth() + 1) }-${ leadZero(today.getDate()) }`,
            end_date: `${ anotherday.getFullYear() }-${ leadZero(anotherday.getMonth() + 1) }-${ leadZero(anotherday.getDate()) }`
        },
        act2: {
            details__name: 'Kvindekrisecentre',
            payment_type: 'RUNNING_PAYMENT',
            start_date: createDate(3),
            payment_frequency: 'WEEKLY',
            payment_cost_type: 'FIXED',
            payment_amount: '12',
            recipient_type: 'COMPANY'
        },
        act3: {
            start_date: createDate(5),
            payment_amount: '15'
        }

    }

fixture('Check payments start date')
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
        .typeText('#field-amount-1', '100', {replace: true})
        .click(Selector('label').withAttribute('for', 'pay-receiver-type-person'))
        .typeText('#field-cpr', '9999999999')
        .click(Selector('label').withAttribute('for', 'pay-method-cash'))
        .click('#activity-submit')
        .expect(Selector('.error-msg').exists).ok()
        .typeText('#pay-date-start', testdata.act1.end_date, {replace: true})
        .click('#activity-submit')
        .expect(Selector('h1').withText('Udgift til').exists).ok()
})

test('Check that an activity may only have one modifier', async t => {

    await createCase(t, testdata.case2)
    await createAppropriation(t, testdata.appr2)
    await createActivity(t, testdata.act2)
    await approveActivities(t)
    
    await t
        .click(Selector('.act-list-row a'))
        .click('.act-edit-btn')
    
    await editActivity(t, testdata.act3)

    await t
        .click(Selector('.act-list-meta-row'))
        .click(Selector('.act-list-sub-row a'))
        .expect(Selector('button').withText('Lav forventet justering').exists).notOk()
})