// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { loginAsUngeraadgiver } from '../utils/logins.js'

const testdata = {
    case1: {
        name: 'xx.xx.xx-testsag'
    },
    appr1: {
        name: 'xx.xx.xx-yy-testbevilling',
        section: 'SEL-109 Botilbud, kriseramte kvinder'
    },
    act1: {
        type: 1,
        act_detail: 'Psykologhjælp til børn',
        start: '2019-08-01',
        end: '2020-12-31',
        note: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
        amount: '3095.50',
        payee_id: '78362883763',
        payee_name: 'Fiktivt Firma ApS'
    },
    act2: {
        type: 0,
        start: '2019-11-01',
        end: '2020-03-31',
        note: 'En lille note',
        amount: '595.95',
        payee_id: '8923',
        payee_name: 'Testbevillingscentralen A/S'
    },
    act3: {
        type: 1,
        start: '2019-11-01',
        end: '2020-03-31',
        note: 'En anden lille note',
        amount: '150',
        payee_id: '8937-2342-2342',
        payee_name: 'TESTiT A/S'
    }
}

fixture `Create some data`// declare the fixture
    .page `http://localhost:8080/#/my-cases/`  // specify the start page

test('Create Case', async t => {

    await loginAsUngeraadgiver(t)
    
    await t
        .click(Selector('button').withText('+ Tilknyt hovedsag'))
        .typeText('#field-sbsys-id', testdata.case1.name)
        .typeText('#field-cpr', '000000-0000')
        .click(Selector('label').withAttribute('for', 'inputRadio1'))
        .click('#selectField4')
        .click(Selector('#selectField4 option').withText('Baltorp'))
        .click('#field-indsatstrappe')
        .click(Selector('#field-indsatstrappe option').withText('Trin 3 - Hjemmebaserede indsatser'))
        .click('#field-skaleringstrappe')
        .click(Selector('#field-skaleringstrappe option').withText('10'))
        .click(Selector('input').withAttribute('type', 'submit'))
        .navigateTo('http://localhost:8080/#/')
        .expect(Selector('.cases table tr:first-child td a').innerText).contains(testdata.case1.name)
})

test('Create Appropriation', async t => {

    await loginAsUngeraadgiver(t)

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('.appropriation-create-btn'))
        .typeText('#field-sbsysid', testdata.appr1.name)
        .click('#field-lawref')
        .click(Selector('#field-lawref option').withText(testdata.appr1.section))
        .click(Selector('input').withAttribute('type', 'submit'))
        .navigateTo('http://localhost:8080/#/')
        .click(Selector('a').withText(testdata.case1.name))
        .expect(Selector('.appropriation-list tr:first-child td a').innerText).contains(testdata.appr1.name)
})

async function createActivity(t, act_data) {
    await t
        .click(Selector('.activities-create-btn'))
        .click('#fieldSelectAct')
        .click(Selector('#fieldSelectAct option').nth(act_data.type))
        .typeText('#field-startdate', act_data.start)
        .typeText('#field-enddate', act_data.end)
        .typeText('#field-text', act_data.note)
        .click('#pay-type-2')
        .typeText('#field-amount-1', act_data.amount)
        .click('#pay-freq')
        .click(Selector('#pay-freq option').nth(1))
        .click('#field-payee')
        .click(Selector('#field-payee option').nth(2))
        .typeText('#field-payee-id', act_data.payee_id)
        .typeText('#field-payee-name', act_data.payee_name)
        .click('#field-pay-method')
        .click(Selector('#field-pay-method option').nth(1))
        .click(Selector('input').withAttribute('type', 'submit'))
}

test('Create Activity', async t => {
    
    await loginAsUngeraadgiver(t)

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))
    
    await createActivity(t, testdata.act1)
    await createActivity(t, testdata.act2)
    await createActivity(t, testdata.act3)

    await t
        .navigateTo('http://localhost:8080/#/')
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))
        .expect(Selector('.activities table tr.act-list-item td a').innerText).contains(testdata.act1.act_detail)
})

test('Approve appropriation', async t => {
    
    await loginAsUngeraadgiver(t)

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))
        .click(Selector('button').withText('Godkend'))
        .click('#inputRadio1')
        .typeText('#field-text', 'Godkendt grundet svære og særligt tvingende omstændigheder')
        .click(Selector('button').withText('Godkend'))
        .expect(Selector('.sagsstatus .label').innerText).contains('bevilget')
})
