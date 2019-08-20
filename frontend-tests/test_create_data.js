// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { user } from './roles.js'

fixture `Create some data`// declare the fixture
    .page `localhost:8080`;  // specify the start page

test('Create Case', async t => {
    
    await t
        .useRole( user )
        .click(Selector('button').withText('+ Tilknyt hovedsag'))
        .typeText('#field-sbsys-id', '24.24.23-testsag')
        .typeText('#field-cpr', '000000-0000')
        .click(Selector('label').withAttribute('for', 'inputRadio1'))
        .click('#selectField4')
        .click(Selector('#selectField4 option').withText('Baltorp'))
        .click('#selectField1')
        .click(Selector('#selectField1 option').withText('Trin 3 - Hjemmebaserede indsatser'))
        .click('#selectField2')
        .click(Selector('#selectField2 option').withText('10'))

        
        .expect(Selector('.msg').nth(1).innerText).contains('Du er logget ud')
})
