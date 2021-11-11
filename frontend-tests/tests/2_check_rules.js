// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { login } from '../utils/logins.js'
import baseurl from '../utils/url.js'
import { leadZero, randNum, createDate } from '../utils/utils.js'
import { createCase, createAppropriation, createActivity, approveActivities, editActivity } from '../utils/crud.js'
import checkConsole from '../utils/console.js'

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
            day_of_month: '4', 
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
        },
        act4: {
            details__name: 'Tolk',
            start_date: createDate(10),
            status: 'EXPECTED',
            payment_type: 'RUNNING_PAYMENT',
            payment_frequency: 'WEEKLY',
            payment_cost_type: 'FIXED',
            payment_amount: '12',
            recipient_type: 'COMPANY'
        }

    }

fixture('Check rules')
    .page(baseurl)
    .beforeEach(async t => { 
        await login(t) 
    })
    .afterEach(() => checkConsole())

test('Start date rule check for activities with "CASH" payment', async t => {

    await createCase(t, testdata.case1)

    await createAppropriation(t, testdata.appr1)

    await t
        .click(Selector('.activities-create-btn'))
        .click('#fieldSelectAct')
        .click(Selector('#fieldSelectAct option').nth(1))
        .typeText('#pay-date-start', testdata.act1.start_today)
        .click('#pay_day_of_month')
        .click(Selector('#pay_day_of_month option').withText(testdata.act1.day_of_month))
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

/*
    Rules to test: (See https://redmine.magenta-aps.dk/issues/41985)
    Activity type can not be edited when creating an EXPECTED activity that modifies an existing activity
*/
test('Check editing of activity type', async t => {

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))

    await createActivity(t, testdata.act4)

    await approveActivities(t)

    // When adding an EXPECTED activity based on a GRANTED activity, we should not be able to edit activity type
    await t
        .click(Selector('a').withText(testdata.act4.details__name))
        .click('.act-edit-btn')
        .expect(Selector('#fieldSelectAct').exists).notOk()
})