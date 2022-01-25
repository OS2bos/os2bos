// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { login } from '../utils/logins.js'
import { createActivity, createAppropriation, createCase, approveActivities } from '../utils/crud.js'
import { axe } from '../utils/axe.js'
import baseurl from '../utils/url.js'
import { makeDateStr, useSelectBox } from '../utils/utils.js'
import checkConsole from '../utils/console.js'

const today = new Date(),
    rand = Math.floor(Math.random() * 1000 ),
    rand2 = Math.floor(Math.random() * 1000 )

const now = makeDateStr(today, 0),
    lastmth = makeDateStr(today, -1),
    str1mth = makeDateStr(today, 1),
    str2mth = makeDateStr(today, 2),
    str5mth = makeDateStr(today, 5),
    str15mth = makeDateStr(today, 15)
    
const testdata = {
    case1: {
        id: 1,
        name: `ex.po.rt-1${ rand }-${ rand2 }`,
        effort_step: '3',
        scaling_step: '6',
        target_group: 'Familieafdelingen',
        district: 'Skovlunde',
        cpr: '0101011100'
    },
    case2: {
        id: 1,
        name: `ex.po.rt-2${ rand2 }-${ rand }`,
        effort_step: '3',
        scaling_step: '6',
        target_group: 'Familieafdelingen',
        district: 'Baltorp',
        cpr: '2323232233'
    },
    appr1: {
        id: 2,
        name: `ex.po.rt-1${ rand }-bevil${ rand2 }`,
        section: 'SEL-54-a Tilknytning af koordinator'
    },
    appr2: {
        id: 2,
        name: `ex.po.rt-2${ rand2 }-bevil${ rand }`,
        section: 'SEL-54-a Tilknytning af koordinator'
    },
    act1: {
        payment_type: 'RUNNING_PAYMENT',
        start_date: str1mth,
        end_date: str5mth,
        payment_frequency: 'WEEKLY',
        payment_cost_type: 'FIXED',
        payment_amount: '20000',
        recipient_type: 'COMPANY'
    },
    act2: {
        payment_type: 'RUNNING_PAYMENT',
        start_date: str1mth,
        end_date: str2mth,
        payment_frequency: 'WEEKLY',
        payment_cost_type: 'FIXED',
        payment_amount: '10000',
        recipient_type: 'COMPANY'
    },
    act3: {
        start_date: str2mth,
        end_date: str15mth,
        payment_amount: '3595.50'
    }
}

fixture.skip('Export DST XML') // declare the fixture
    .page(baseurl)  // specify the start page
    .afterEach(() => checkConsole())

test('Create data and check in export list', async t => {

    await login(t, 'familieleder', 'sagsbehandler')

    await createCase(t, testdata.case1)
    await createAppropriation(t, testdata.appr1)
    await createActivity(t, testdata.act1)
    await approveActivities(t)

    await t.navigateTo(baseurl)
    await createCase(t, testdata.case2)
    await createAppropriation(t, testdata.appr2)
    await createActivity(t, testdata.act2)
    await approveActivities(t)

    await t
        .navigateTo(baseurl + '/#/export')
        // List should be empty as default
        .expect(Selector('.datagrid-action > a').withText(testdata.appr1.name).exists).notOk()
        .expect(Selector('.datagrid-action > a').withText(testdata.appr2.name).exists).notOk()
    
    // Change section filters and notice that our new appropriations appear in list
    await useSelectBox(t,'#field-section', 'SEL-54-a Tilknytning af koordinator')
    await axe(t)
    
    await t
        .expect(Selector('.datagrid-action > a').withText(testdata.appr1.name).exists).ok()
        .expect(Selector('.datagrid-action > a').withText(testdata.appr2.name).exists).ok()
})
