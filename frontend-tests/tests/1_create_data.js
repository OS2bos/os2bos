// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { login } from '../utils/logins.js'
import { createActivity, editActivity, createAppropriation, createCase } from '../utils/crud.js'
import { axe } from '../utils/axe.js'
import baseurl from '../utils/url.js'
import { makeDateStr, useSelectBox } from '../utils/utils.js'
import checkConsole from '../utils/console.js'

let today = new Date(),
    rand = Math.floor(Math.random() * 1000 ),
    rand2 = Math.floor(Math.random() * 1000 )

let str1mth = makeDateStr(today, 1),
    str2mth = makeDateStr(today, 2),
    str5mth = makeDateStr(today, 5),
    str10mth = makeDateStr(today, 10),
    str15mth = makeDateStr(today, 15)
    
const testdata = {
    case1: {
        id: 1,
        name: `xx.xx.xx-${ rand }-${ rand2 }`,
        effort_step: '3',
        scaling_step: '6',
        target_group: 'Familieafdelingen',
        district: 'Baltorp'
    },
    appr1: {
        id: 1,
        name: `xx.xx.xx-${ rand }-${ rand2 }-bevil${ rand }`,
        section: 'SEL-52-3.9 Anden hjælp'
    },
    appr2: {
        id: 2,
        name: `yy.yy.yy-${ rand2 }-bevil${ rand }`,
        section: 'SEL-54-a Tilknytning af koordinator'
    },
    appr3: {
        id: 3,
        name: `${ rand2 }.zz.zz-${ rand }-bevil${ rand2 }`,
        section: 'SEL-52-3.4 Døgnophold for hele familien'
    },
    act1: {
        note: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
        payment_type: 'RUNNING_PAYMENT',
        start_date: str1mth,
        end_date: str10mth,
        payment_frequency: 'MONTHLY',
        pay_day_of_month: '2',
        payment_cost_type: 'FIXED',
        payment_amount: '3095.50',
        recipient_type: 'COMPANY',
        details__name: 'Kvindekrisecentre'
    },
    act2: {
        details__name: 'Tolk',
        payment_type: 'RUNNING_PAYMENT',
        start_date: str2mth,
        end_date: str5mth,
        payment_frequency: 'MONTHLY',
        pay_day_of_month: '1',
        payment_cost_type: 'FIXED',
        recipient_type: 'COMPANY',
        payment_amount: '595.95'
    },
    act3: {
        details__name: 'Tolk',
        note: 'En anden lille note',
        payment_type: 'ONE_TIME_PAYMENT',
        payment_date: str5mth,
        payment_cost_type: 'FIXED',
        payment_amount: '150',
        recipient_type: 'PERSON',
        recipient_id: '777777-7777',
        payment_method: 'SD'
    },
    act4: {
        start_date: str2mth,
        end_date: str15mth,
        payment_amount: '3595.50'
    },
    act5: {
        details__name: 'Egenbetaling',
        status: 'EXPECTED',
        payment_type: 'RUNNING_PAYMENT',
        payment_frequency: 'WEEKLY',
        start_date: str2mth,
        end_date: str5mth,
        note: 'En anden lille note',
        payment_cost_type: 'FIXED',
        payment_amount: '9.95',
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
        payment_cost_type: 'FIXED',
        payment_amount: '999.95',
        recipient_type: 'COMPANY'
    }
}

fixture('Login and create some data') // declare the fixture
    .page(baseurl)  // specify the start page
    .beforeEach(async t => { 
        await login(t)
    })
    .afterEach(() => checkConsole())

test('Create case and appropriation', async t => {
    
    await axe(t)

    await createCase(t, testdata.case1)

    await axe(t)

    await createAppropriation(t, testdata.appr1)

    await axe(t)

    await t.expect(Selector('.crumb-2 span').innerText).contains(testdata.appr1.name)
})


// Issue describing rule to test
// https://redmine.magenta-aps.dk/issues/48204
test('Edit appropriation paragraph', async t => {

    await t
        .navigateTo(`${baseurl}/#/appropriations/`)
        .typeText('#field-sbsysid', testdata.appr1.name, {replace: true})
        .click(`.datagrid-action[title="${testdata.appr1.name}"] a`)
        .click('.appr-edit-btn')
        
    // Should be able to change paragraph while the appropriation is still in draft mode
    await useSelectBox(t, '#field-lawref', 'SEL-109 Botilbud, kriseramte kvinder')

    await t
        .click('.form-actions input[type="submit"]')
        .expect(Selector('dd').withText('SEL-109 Botilbud, kriseramte kvinder').exists).ok()
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

    await t.expect(Selector('.act-list-row a').exists).ok()
    
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

// Issue describing rule to test
// https://redmine.magenta-aps.dk/issues/48204
test('Edit appropriation paragraph after approval', async t => {

    await t
        .navigateTo(`${baseurl}/#/appropriations/`)
        .typeText('#field-sbsysid', testdata.appr1.name, {replace: true})
        .click(`td.datagrid-action[title="${testdata.appr1.name}"] a`)
        .click('.appr-edit-btn')
        // Should not be able to change paragraph since the appropriation has been approved
        .expect(Selector('#field-lawref').hasAttribute('disabled')).ok()
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
        .expect(Selector('h1').withText('Bevillingsskrivelse').exists).ok()
        .expect(Selector('.label-EXPECTED').exists).ok()
    
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
    
    await createAppropriation(t, testdata.appr2)
        
    await t
        .click(Selector('a.header-link'))
        .click(Selector('a').withText(testdata.case1.name))
        .expect(Selector('.datagrid-action > a').withText(testdata.appr2.name).exists).ok()
})

test('Create activities with one main activity option', async t => {

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr2.name))
    
    await createActivity(t, testdata.act7)

    await axe(t)

    await t.expect(Selector('.act-list-row a').exists).ok()
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
