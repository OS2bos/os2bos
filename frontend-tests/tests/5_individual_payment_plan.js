// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { familieleder } from '../utils/logins.js'
import { createActivity, createPayment, approveActivities } from '../utils/crud.js'
import baseurl from '../utils/url.js'
import { makeDateStr, leadZero } from '../utils/utils.js'
import checkConsole from '../utils/console.js'
import { appr5 } from '../testdata.js'

function nextdays(date, offset) {
    let new_date = new Date(date.setDate(date.getDate() + offset + 1))
    return `${new_date.getFullYear()}-${leadZero(new_date.getMonth() + 1)}-${leadZero(new_date.getDate())}`
}

let today = new Date()

let strday1 = nextdays(today, 1),
    strday2 = nextdays(today, 2),
    str5mth = makeDateStr(today, 5)
    
const testdata = {
    act1: {
        details__name: 'Kvindekrisecentre',
        payment_type: 'INDIVIDUAL_PAYMENT',
        start_date: strday1,
        recipient_type: 'COMPANY'
    },
    act2: {
        details__name: 'Tolk',
        payment_type: 'RUNNING_PAYMENT',
        start_date: strday1,
        end_date: str5mth,
        payment_frequency: 'WEEKLY',
        payment_cost_type: 'FIXED',
        payment_amount: '12.95',
        recipient_type: 'COMPANY'
    },
    act3: {
        details__name: 'Tolk',
        payment_type: 'ONE_TIME_PAYMENT',
        payment_date: str5mth,
        payment_cost_type: 'FIXED',
        payment_amount: '15',
        recipient_type: 'PERSON',
        recipient_id: '777777-7777',
        payment_method: 'SD'
    },
    payment1: {
        amount: '100',
        date: strday1
    },
    payment2: {
        amount: '101.10',
        date: strday2
    }
}

fixture('Activities with individual payment plan') // declare the fixture
    .beforeEach(async t => { 
        await t.useRole(familieleder)
    })
    .page(baseurl)  // specify the start page
    .afterEach(() => checkConsole())

test('Create activities', async t => {

    await t.navigateTo(`${ baseurl }/#/appropriation/${ appr5.id }/`)

    await createActivity(t, testdata.act1)
    await createActivity(t, testdata.act2)
    await createActivity(t, testdata.act3)

    await t
        .click(Selector('a').withText(testdata.act3.details__name))
        .expect(Selector('.payment-create-btn').exists).notOk()
        .click(Selector('a').withText(appr5.sbsys_id))
        .click(Selector('a').withText(testdata.act2.details__name))
        .expect(Selector('.payment-create-btn').exists).notOk()
        .click(Selector('a').withText(appr5.sbsys_id))
        .click(Selector('a').withText(testdata.act1.details__name))
        .expect(Selector('.payment-create-btn').exists).ok()
})

test('Add new payments', async t => {

    await t.navigateTo(`${ baseurl }/#/appropriation/${ appr5.id }/`)
    
    await t.click(Selector('a').withText(testdata.act1.details__name))
        
    await createPayment(t, testdata.payment1)
    await createPayment(t, testdata.payment2)

    await t.expect(Selector('p').withText('Viser').innerText).contains('2')
})

test('Edit payment', async t => {

    await t.navigateTo(`${ baseurl }/#/appropriation/${ appr5.id }/`)

    await t
        .click(Selector('a').withText(testdata.act1.details__name))
        .click(Selector('button').withText('#').nth(1))
        .typeText('#field-planned-amount', '99.99', {replace: true})
        .click(Selector('input').withAttribute('value', 'Opdatér'))
        .expect(Selector('td').withAttribute('title', '99.99').exists).ok()
})

test('Delete payment', async t => {

    await t.navigateTo(`${ baseurl }/#/appropriation/${ appr5.id }/`)

    await t
        .click(Selector('a').withText(testdata.act1.details__name))
        .click(Selector('button').withText('#').nth(1))
        .click(Selector('.payment-delete-btn'))
        .click(Selector('#payment-confirm-delete'))
        .expect(Selector('p').withText('Viser').innerText).contains('1')
})

test('Approve and notice that no further payments can be added', async t => {
    
    await t.navigateTo(`${ baseurl }/#/appropriation/${ appr5.id }/`)
        
    await approveActivities(t)

    await t.expect(Selector('.payment-create-btn').exists).notOk()
})