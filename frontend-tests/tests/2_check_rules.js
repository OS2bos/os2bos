// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { login } from '../utils/logins.js'
import baseurl from '../utils/url.js'
import { leadZero, randNum } from '../utils/utils.js'

const today = new Date(),
    tomorrow = new Date(new Date().setDate(today.getDate() + 2)),
    testdata = {
        case: {
            name: `${ randNum() }.${ randNum() }.${ randNum() }-regel-test`
        },
        appr: {
            name: `${ randNum() }.${ randNum() }.${ randNum() }-regel-test-bevilling`
        },
        act: {
            start_today: `${ today.getFullYear() }-${ leadZero(today.getMonth() + 1) }-${ leadZero(today.getDate()) }`,
            start_tomorrow: `${ tomorrow.getFullYear() }-${ leadZero(tomorrow.getMonth() + 1) }-${ leadZero(tomorrow.getDate()) }`
        }
    }

fixture `Check payments start date`
    .page(baseurl)
    .beforeEach(async t => { 
        await login(t) 
    })

test('Start date rule check for activities with "CASH" payment', async t => {

    await t
        .click(Selector('button').withText('+ Tilknyt hovedsag'))
        .typeText('#field-sbsys-id', testdata.case.name)
        .typeText('#field-cpr', '000000-0000')
        .click(Selector('label').withAttribute('for', 'inputRadio1'))
        .click('#selectField4')
        .click(Selector('#selectField4 option').withText('Baltorp'))
        .click('#field-indsatstrappe')
        .click(Selector('#field-indsatstrappe option').withText('Trin 3: Hjemmebaserede indsatser'))
        .click('#field-skaleringstrappe')
        .click(Selector('#field-skaleringstrappe option').withText('5'))
        .click(Selector('input').withAttribute('type', 'submit'))
        .click(Selector('.appropriation-create-btn'))
    
        .typeText('#field-sbsysid', testdata.appr.name)
        .click('#field-lawref')
        .click(Selector('#field-lawref option').nth(1))
        .click(Selector('input').withAttribute('type', 'submit'))
        .click(Selector('.activities-create-btn'))
        .click('#fieldSelectAct')
        .click(Selector('#fieldSelectAct option').nth(1))
        .typeText('#field-startdate', testdata.act.start_today)
        .click('#field-payee')
        .click(Selector('#field-payee option').nth(2))
        .click('#field-pay-method')
        .click(Selector('#field-pay-method option').nth(0))
        .expect(Selector('.warning').exists).ok()
        .typeText('#field-startdate', testdata.act.start_tomorrow)
        .expect(Selector('.warning').exists).notOk()
})