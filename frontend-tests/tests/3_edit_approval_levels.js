// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { login } from '../utils/logins.js'
import { createActivity } from '../utils/crud.js'
import { axe, axeOptions } from '../utils/axe.js'
import baseurl from '../utils/url.js'

fixture('Adding approval levels') // declare the fixture
    .page(baseurl)  // specify the start page
    .beforeEach(async t => { 
        await login(t, 'admin', 'sagsbehandler')
    })

test.skip.page('')
('Add new approval level in Django admin', async t => {
    
    //await t.click(Selector('button').withText('+ Tilknyt hovedsag'))
    
    //await axe(t, null, axeOptions)

    
})
