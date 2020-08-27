// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { login } from '../utils/logins.js'
import { createCase } from '../utils/crud.js'
import baseurl from '../utils/url.js'

let rand = Math.floor(Math.random() * 1000 ),
    rand2 = Math.floor(Math.random() * 1000 )
    
const target_group_name = `testmålgruppe-${ rand }`,
    testdata = {
        case1: {
            id: 1,
            name: `x${ rand }.y${ rand2 }.yy`,
            target_group: target_group_name
        },
        case2: {
            id: 1,
            name: `x${ rand }.z${ rand2 }.${ rand2 }`,
            effort_step: '3',
            scaling_step: '5',
            target_group: 'Handicapafdelingen'
        }
    }

fixture('Check appropriation paragraph choices') // declare the fixture
    .page(baseurl)  // specify the start page

test('Add new target group in Django admin', async t => {

    await login(t, 'admin', 'admin')

    await t
        .navigateTo('/api/admin/core/targetgroup/add/')
        .typeText('#id_name', target_group_name)
        .click(Selector('input').withAttribute('name', '_save'))
        .expect(Selector('a').withText(target_group_name).exists).ok()
})

test('Appropriation with 0 available paragraphs should display all paragraphs as default', async t => {

    await login(t, 'familieleder', 'sagsbehandler')
    
    await createCase(t, testdata.case1)

    await t
        .click(Selector('.appropriation-create-btn'))
        .click(Selector('#field-lawref'))
        .expect(Selector('#field-lawref option').nth(0).innerText).contains('SEL-10')
        .expect(Selector('#field-lawref option').nth(145).exists).ok()
})

test('Add target group to paragraph in Django admin', async t => {

    await login(t, 'admin', 'admin')

    await t
        .navigateTo('/api/admin/core/section/1249/change/')
        .click('#id_allowed_for_target_groups_add_all_link')
        .click(Selector('input').withAttribute('name', '_save'))
})

test('Appropriation with 1 available paragraph should display no selectbox', async t => {

    await login(t, 'familieleder', 'sagsbehandler')

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('.appropriation-create-btn'))
        .expect(Selector('#field-lawref').exists).notOk()
})

test('Appropriation with some available paragraphs should display only those paragraphs', async t => {

    await login(t, 'familieleder', 'sagsbehandler')
    
    await createCase(t, testdata.case2)

    await t
        .click(Selector('.appropriation-create-btn'))
        .click(Selector('#field-lawref'))
        .expect(Selector('#field-lawref option').nth(0).innerText).contains('SEL-109')
        .expect(Selector('#field-lawref option').nth(145).exists).notOk()
})