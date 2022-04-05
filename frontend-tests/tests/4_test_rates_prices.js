// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { familieleder } from '../utils/logins.js'
import { makeDateStr } from '../utils/utils.js'
import { createActivity, approveActivities } from '../utils/crud.js'
import baseurl from '../utils/url.js'
import checkConsole from '../utils/console.js'
import { appr4 } from '../testdata.js'

let today = new Date()

let str1mth = makeDateStr(today, 1),
    str2mth = makeDateStr(today, 2),
    str5mth = makeDateStr(today, 5),
    str10mth = makeDateStr(today, 10)
    
const testdata = {
    act1: {
        payment_type: 'RUNNING_PAYMENT',
        start_date: str1mth,
        end_date: str10mth,
        payment_frequency: 'MONTHLY',
        pay_day_of_month: '2',
        payment_cost_type: 'GLOBAL_RATE',
        payment_units: '6',
        recipient_type: 'COMPANY',
        details__name: 'Kvindekrisecentre'
    },
    act2: {
        details__name: 'Tolk',
        payment_type: 'RUNNING_PAYMENT',
        start_date: str2mth,
        end_date: str5mth,
        payment_frequency: 'WEEKLY',
        payment_cost_type: 'PER_UNIT',
        payment_units: '28',
        recipient_type: 'COMPANY',
        price_amount: '2280',
        price_start_date: str2mth
    }
}

fixture('Test editing rates and prices') // declare the fixture
    .beforeEach(async t => { 
        await t.useRole(familieleder)
    })
    .page(baseurl)  // specify the start page
    .afterEach(() => checkConsole())

test('Create activity with global rate', async t => {

    await t.navigateTo(`${ baseurl }/#/appropriation/${ appr4.id }/`)

    await createActivity(t, testdata.act1)
    
    await t.expect(Selector('.act-list-row a').withText(testdata.act1.details__name.substring(0,4)).exists).ok()
})

test('Create activity with per unit pricing', async t => {
    
    await t.navigateTo(`${ baseurl }/#/appropriation/${ appr4.id }/`)

    await createActivity(t, testdata.act2)

    const act_link_text = testdata.act2.details__name.substring(0,3)
    
    await t
        .expect(Selector('.act-list-row a').withText(act_link_text).exists).ok()
        .click(Selector('.act-list-row a').withText(act_link_text))
        .click(Selector('.act-edit-btn'))
        .typeText('#pay-units', '30.5', {replace: true}) // Edit units
        .click('input[type="submit"]')
        .expect(Selector('h1').withText('Udgift til').exists).ok() // Expect to save with no trouble
        .click(Selector('.act-edit-btn'))
        .click('.prices-history button')
        .typeText('#pay-cost-pr-unit', '3000', {replace: true}) // Edit price
        .typeText('#pay-cost-exec-date', str10mth) // Set a date
        .click('.modal-footer input[type="submit"]')
        .click('input[type="submit"]')
        .expect(Selector('h1').withText('Udgift til').exists).ok() // Expect to save with no trouble
        .click(Selector('a').withText('Bevillingsskrivelse'))

    await approveActivities(t)

    await t
        .click(Selector('.act-list-row a').withText(act_link_text))
        .expect(Selector('.perunitdisplay').innerText).contains('2.280,00 kr x 30,50')  // price and unit should be visible and correct after approve 

})
