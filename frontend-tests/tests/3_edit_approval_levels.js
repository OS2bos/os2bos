// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { login } from '../utils/logins.js'
import { createActivity } from '../utils/crud.js'
import { axe, axeOptions } from '../utils/axe.js'
import baseurl from '../utils/url.js'

let appro_lvl_name = 'etaten'

fixture('Adding approval levels') // declare the fixture
    .page(baseurl)  // specify the start page

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

    await t
        .click(Selector('a').withAttribute('href', '#/'))
        .click(Selector('td.datagrid-action a'))
        .click(Selector('td.datagrid-action a'))
        .click(Selector('label').withAttribute('for', 'check-all'))
        .click(Selector('button').withText('Godkend valgte'))
        .expect(Selector('label').withText(appro_lvl_name[0].toUpperCase()).exists).ok()

})
