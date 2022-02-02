// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { familieleder } from '../utils/logins.js'
import { makeDateStr } from '../utils/utils.js'
import { createActivity, createCase, createAppropriation, approveActivities } from '../utils/crud.js'
import baseurl from '../utils/url.js'
import checkConsole from '../utils/console.js'

let today = new Date(),
    rand = Math.floor(Math.random() * 500 ),
    rand2 = Math.floor(Math.random() * 500 )

let str1mth = makeDateStr(today, 1),
    str2mth = makeDateStr(today, 2),
    str5mth = makeDateStr(today, 5),
    str10mth = makeDateStr(today, 10)
    
const testdata = {
    case1: {
        id: 1,
        name: `${ rand2 }.${ rand }.xx`,
        effort_step: '3',
        scaling_step: '4',
        target_group: 'Handicapafdelingen'
    },
    appr1: {
        id: 1,
        name: `${ rand2 }.${ rand }.xx-${ rand2 }-bevil${ rand }`,
        section: 'SEL-109 Botilbud, kriseramte kvinder'
    },
    act1: {
        note: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.',
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
    .page(baseurl)  // specify the start page
    .beforeEach(async t => { 
        await t.useRole(familieleder)
    })
    .afterEach(() => checkConsole())

test('Create case, appropriation, and activity with global rate', async t => {
    await createCase(t, testdata.case1)
    await createAppropriation(t, testdata.appr1)
    await createActivity(t, testdata.act1)
    
    await t.expect(Selector('.act-list-row a').withText(testdata.act1.details__name.substr(0,4)).exists).ok()
})

test('Create activity with per unit pricing', async t => {
    await t
        .click(Selector('a.header-link'))
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))

    await createActivity(t, testdata.act2)

    const act_link_text = testdata.act2.details__name.substr(0,3)
    
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
