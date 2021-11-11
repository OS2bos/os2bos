// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { login } from '../utils/logins.js'
import baseurl from '../utils/url.js'
import { makeDateStr } from '../utils/utils.js'
import { createActivity, createAppropriation, createCase } from '../utils/crud.js'
import checkConsole from '../utils/console.js'

let today = new Date(),
    rand = Math.floor(Math.random() * 1000 ),
    rand2 = Math.floor(Math.random() * 1000 ),
    appro_lvl_name = 'etaten'

let str1mth = makeDateStr(today, 1),
    str10mth = makeDateStr(today, 10)
    
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
        section: 'SEL-109 Botilbud, kriseramte kvinder'
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
    }
}

fixture('Adding approval levels') // declare the fixture
    .page(baseurl)  // specify the start page
    .afterEach(() => checkConsole())

test('Add new approval level in Django admin', async t => {

    await login(t, 'admin', 'admin')

    await t
        .click(Selector('a').withAttribute('href', '/api/admin/'))
        .click(Selector('a').withAttribute('href', '/api/admin/core/approvallevel/add/'))
        .typeText('#id_name', appro_lvl_name)
        .click(Selector('input').withAttribute('name', '_save'))
        .expect(Selector('a').withText(appro_lvl_name).exists).ok()

})

test('Check existence of approval level', async t => {

    await login(t, 'familieleder', 'sagsbehandler')

    await createCase(t, testdata.case1)
    await createAppropriation(t, testdata.appr1)
    await createActivity(t, testdata.act1)

    await t
        .click(Selector('label').withAttribute('for', 'check-all'))
        .click(Selector('button').withText('Godkend valgte'))
        .expect(Selector('label').withText(appro_lvl_name[0].toUpperCase()).exists).ok()
})
