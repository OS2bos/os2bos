// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { login } from '../utils/logins.js'
import { createActivity, editActivity } from '../utils/crud.js'
import { axe } from '../utils/axe.js'
import baseurl from '../utils/url.js'

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

let today = new Date(),
    rand = Math.floor(Math.random() * 100 )

let str1mth = makeDateStr(today, 1),
    str2mth = makeDateStr(today, 2),
    str5mth = makeDateStr(today, 5),
    str10mth = makeDateStr(today, 10),
    str15mth = makeDateStr(today, 15)
    
const testdata = {
    case1: {
        id: 1,
        name: `xx.xx.xx-${ rand }-yy`
    },
    appr1: {
        id: 1,
        name: `xx.xx.xx-${ rand }-bevil${ rand }`,
        section: 'SEL-109 Botilbud, kriseramte kvinder'
    },
    appr2: {
        id: 2,
        name: `xx.xx.xx-${ rand }-bevil${ rand }`,
        section: 'SEL-54-a Tilknytning af koordinator'
    },
    appr3: {
        id: 3,
        name: `${ rand }.xx.xx-${ rand }-bevil${ rand }`,
        section: 'SEL-52-3.4 Døgnophold for hele familien'
    },
    act1: {
        note: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
        payment_type: 'RUNNING_PAYMENT',
        start_date: str1mth,
        end_date: str10mth,
        payment_frequency: 'MONTHLY',
        pay_day_of_month: '2',
        amount: '3095.50',
        recipient_type: 'COMPANY',
        recipient_name: 'Base Camp',
        recipient_id: '12341234',
        details__name: 'Kvindekrisecentre'
    },
    act2: {
        details__name: 'Tolk',
        payment_type: 'RUNNING_PAYMENT',
        start_date: str2mth,
        end_date: str5mth,
        payment_frequency: 'MONTHLY',
        pay_day_of_month: '1',
        amount: '595.95',
        recipient_type: 'COMPANY',
        recipient_id: '89238762',
        recipient_name: 'Testbevillingscentralen A/S',
    },
    act3: {
        note: 'En anden lille note',
        payment_type: 'ONE_TIME_PAYMENT',
        start_date: str5mth,
        end_date: str10mth,
        amount: '150',
        recipient_type: 'PERSON',
        recipient_id: '777777-7777',
        payment_method: 'SD'
    },
    act4: {
        start_date: str2mth,
        end_date: str15mth,
        amount: '3595.50'
    },
    act5: {
        status: 'EXPECTED',
        payment_type: 'RUNNING_PAYMENT',
        payment_frequency: 'WEEKLY',
        start_date: str2mth,
        end_date: str5mth,
        note: 'En anden lille note',
        amount: '9.95',
        recipient_type: 'INTERNAL',
        recipient_id: 'xxxx-xxxx',
        recipient_name: 'Familiehuset'
    },
    act7: {
        start_date: str2mth,
        end_date: str5mth,
        payment_type: 'RUNNING_PAYMENT',
        payment_frequency: 'BIWEEKLY',
        note: 'Denne ydelse vil blive slettet',
        amount: '999.95',
        recipient_type: 'COMPANY',
        recipient_id: '89372342',
        recipient_name: 'TESTiT A/S'
    }
}

fixture('Login and create some data') // declare the fixture
    .page(baseurl)  // specify the start page
    .beforeEach(async t => { 
        await login(t)
    })

test('Create case and appropriation', async t => {
    
    await t.click(Selector('button').withText('+ Tilknyt hovedsag'))
    
    await axe(t)

    await t
        .typeText('#field-sbsys-id', testdata.case1.name)
        .typeText('#field-cpr', '000000-0000')
        .click('#selectTargetGroup')
        .click(Selector('#selectTargetGroup option').withText('Familieafdelingen'))
        .click('#selectDistrict')
        .click(Selector('#selectDistrict option').withText('Baltorp'))
        .click('#field-indsatstrappe')
        .click(Selector('#field-indsatstrappe option').withText('Trin 3: Hjemmebaserede indsatser'))
        .click('#field-skaleringstrappe')
        .click(Selector('#field-skaleringstrappe option').withText('5'))
        .click(Selector('input').withAttribute('type', 'submit'))
        .click(Selector('a.header-link'))
        .expect(Selector('.cases table a').withText(testdata.case1.name)).ok()
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('.appropriation-create-btn'))
        .typeText('#field-sbsysid', testdata.appr1.name)
        .click('#field-lawref')
        .click(Selector('#field-lawref option').withText(testdata.appr1.section))
    
    await axe(t)

    await t
        .click(Selector('input').withAttribute('type', 'submit'))
        .click(Selector('a.header-link'))
        .click(Selector('a').withText(testdata.case1.name))
        .expect(Selector('.datagrid-action a').innerText).contains(testdata.appr1.name)
    
    await axe(t)
})

test('Create activities', async t => {

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))
    
    await createActivity(t, testdata.act1)
    await createActivity(t, testdata.act2)
    await createActivity(t, testdata.act3)

    await t
        .click(Selector('a.header-link'))
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))

    await t.expect(Selector('.activities table tr.act-list-item a').exists).ok()
    
    await axe(t)
})

test('Approve appropriation', async t => {

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))
        .click('#check-all')
        .click(Selector('button').withText('Godkend valgte'))
    
    await axe(t)

    await t
        .click(Selector('label').withAttribute('for','radio-btn-1'))
        .typeText('#field-text', 'Godkendt grundet svære og særligt tvingende omstændigheder')
        .click('button[type="submit"]')
        .expect(Selector('.mini-label .label-GRANTED').exists).ok()
    
    await axe(t)
})

test('Add adjustment activities', async t => {
    
    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))
        .click(Selector('a').withText(testdata.act1.details__name))
        .click('.act-edit-btn')
    
    await editActivity(t, testdata.act4)

    await t
        .click(Selector('a.header-link'))
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))
    
    await createActivity(t, testdata.act5)
    
    await t
        .expect(Selector('.label-EXPECTED')).ok()
        .expect(Selector('h1').withText('Bevillingsskrivelse').exists).ok()
    
    await axe(t)
})

test('Delete appropriation draft', async t => {

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('.appropriation-create-btn'))
    
    await axe(t)

    await t
        .typeText('#field-sbsysid', testdata.appr3.name)
        .click('#field-lawref')
        .click(Selector('#field-lawref option').withText(testdata.appr3.section))
        .click(Selector('input').withAttribute('type', 'submit'))
        .click(Selector('.appr-delete-btn'))
        .click(Selector('.modal-delete-btn'))
    
    await axe(t)
})

test('Create appropriation with one main activity option', async t => {

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('.appropriation-create-btn'))
    
    await axe(t)

    await t
        .typeText('#field-sbsysid', testdata.appr2.name)
        .click('#field-lawref')
        .click(Selector('#field-lawref option').withText(testdata.appr2.section))
        .click(Selector('input').withAttribute('type', 'submit'))
        .click(Selector('a.header-link'))
        .click(Selector('a').withText(testdata.case1.name))
        .expect(Selector('.datagrid-action a').innerText).contains(testdata.appr2.name)
    
    await axe(t)
})

test('Create activities with one main activity option', async t => {

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr2.name))
    
    await createActivity(t, testdata.act7)

    await t
        .click(Selector('a.header-link'))
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr2.name))
        .expect(Selector('.activities table tr.act-list-item a').exists).ok()
    
    await axe(t)
})

test('Approve appropriation with one main activity option', async t => {

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr2.name))
        .click('#check-all')
        .click(Selector('button').withText('Godkend valgte'))
    
    await axe(t)

    await t
        .click(Selector('label').withAttribute('for','radio-btn-3'))
        .typeText('#field-text', 'Godkendt grundet svære omstændigheder')
        .click('button[type="submit"]')
        .expect(Selector('.mini-label .label-GRANTED').exists).ok()
    
    await axe(t)
})
