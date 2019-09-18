// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { loginAsUngeraadgiver } from '../utils/logins.js'

function leadZero(number) {
    if (number < 10) {
        return `0${ number }`
    } else {
        return number
    }
}

function makeDateStr(date, offset) {
    let new_date = new Date(date.setMonth(date.getMonth() + offset + 1))
    return `${new_date.getFullYear()}-${leadZero(new_date.getMonth() + 1)}-01`
}

let today = new Date()

let str1mth = makeDateStr(today, 1),
    str2mth = makeDateStr(today, 2),
    str5mth = makeDateStr(today, 5),
    str10mth = makeDateStr(today, 10),
    str15mth = makeDateStr(today, 15)
    
const testdata = {
    case1: {
        id: 1,
        name: 'xx.xx.xx-testsag'
    },
    appr1: {
        id: 1,
        name: 'xx.xx.xx-yy-testbevilling',
        section: 'SEL-109 Botilbud, kriseramte kvinder'
    },
    act1: {
        type: 1,
        act_detail: 'Psykologhjælp til børn',
        start: str1mth,
        end: str10mth,
        note: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
        amount: '3095.50',
        payee_id: '78362883763',
        payee_name: 'Fiktivt Firma ApS'
    },
    act2: {
        type: 0,
        start: str2mth,
        end: str5mth,
        note: 'En lille note',
        amount: '595.95',
        payee_id: '8923',
        payee_name: 'Testbevillingscentralen A/S'
    },
    act3: {
        type: 1,
        start: str5mth,
        end: str10mth,
        note: 'En anden lille note',
        amount: '150',
        payee_id: '8937-2342-2342',
        payee_name: 'TESTiT A/S'
    },
    act4: {
        expected_type: 'adjustment',
        type: 1,
        start: str2mth,
        end: str15mth,
        note: 'Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
        amount: '3595.50',
        payee_id: '78362883763',
        payee_name: 'Fiktivt Firma ApS'
    },
    act5: {
        expected_type: 'expectation',
        type: 1,
        start: str2mth,
        end: str5mth,
        note: 'En anden lille note',
        amount: '9.95',
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
        .expect(Selector('.cases table a').withText(testdata.case1.name)).ok()
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

    if (act_data.expected_type === 'adjustment') {
        await t.click(Selector('.act-edit-btn'))
    } else {
        await t.click(Selector('.activities-create-btn'))
    }

    if (act_data.expected_type === 'expectation') {
        await t.click(Selector('label').withAttribute('for', 'field-status-expected'))
    }

    await t
        .click('#fieldSelectAct')
        .click(Selector('#fieldSelectAct option').nth(act_data.type))
        .typeText('#field-startdate', act_data.start)
        .typeText('#field-enddate', act_data.end)
        .typeText('#field-text', act_data.note)
        .click('#pay-type-2')
        .typeText('#field-amount-1', act_data.amount)
        .click('#pay-freq')
        .click(Selector('#pay-freq option').withAttribute('value', 'MONTHLY'))
        .click('#pay-day-of-month')
        .click(Selector('#pay-day-of-month option').nth(1))
        .click('#field-payee')
        .click(Selector('#field-payee option').nth(1))
        .typeText('#field-payee-id', act_data.payee_id)
        .typeText('#field-payee-name', act_data.payee_name)
        .click('#field-pay-method')
        .click(Selector('#field-pay-method option').nth(0))
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
        .expect(Selector('.activities table tr.act-list-item a')).ok()
})

test('Approve appropriation', async t => {
    
    await loginAsUngeraadgiver(t)

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))
        .click('#check-all')
        .click(Selector('button').withText('Godkendt valgte'))
        .click(Selector('label').withAttribute('for','inputRadio1'))
        .typeText('#field-text', 'Godkendt grundet svære og særligt tvingende omstændigheder')
        .click(Selector('button').withText('Godkend'))
        .expect(Selector('.mini-label .label-GRANTED')).ok()
})

test('Add adjustment activities', async t => {
    
    await loginAsUngeraadgiver(t)
    
    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))
        .click(Selector('a').withText(testdata.act1.act_detail))
    
    await createActivity(t, testdata.act4)

    await t
        .navigateTo('http://localhost:8080/#/')
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))
    
    await createActivity(t, testdata.act5)
    
    await t.expect(Selector('.label-EXPECTED')).ok()
})
