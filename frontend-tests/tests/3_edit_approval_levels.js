// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { familieleder } from '../utils/logins.js'
import baseurl from '../utils/url.js'
import { makeDateStr } from '../utils/utils.js'
import { createActivity } from '../utils/crud.js'
import checkConsole from '../utils/console.js'
import { appr3 } from '../testdata.js'

let today = new Date(),
    appro_lvl_name = 'etaten'

let str1mth = makeDateStr(today, 1),
    str10mth = makeDateStr(today, 10)
    
const testdata = {
    act1: {
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
    .afterEach(() => checkConsole())

test
    .page(`${baseurl}/api/admin/core/approvallevel/add/`)
    ('Add new approval level in Django admin', async t => {

    if (Selector('.logintext').exists) {
        await t
            .typeText('#username', 'admin')
            .typeText('#password', 'admin')
            .click(Selector('button').withExactText('Login'))
    }

    await t
        .typeText('#id_name', appro_lvl_name)
        .click(Selector('input').withAttribute('name', '_save'))
        .expect(Selector('a').withText(appro_lvl_name).exists).ok()

})

test
    .before(async t => {
        await t.useRole(familieleder)
    })
    .page(baseurl)
    ('Check existence of approval level', async t => {

    await t.navigateTo(`${ baseurl }/#/appropriation/${ appr3.id }/`)

    await createActivity(t, testdata.act1)

    await t
        .click(Selector('label').withAttribute('for', 'check-all'))
        .click(Selector('button').withText('Godkend valgte'))
        .expect(Selector('label').withText(appro_lvl_name[0].toUpperCase()).exists).ok()
})
