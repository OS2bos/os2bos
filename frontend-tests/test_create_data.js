// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { user } from './roles.js'

fixture `Create some data`// declare the fixture
    .page `localhost:8080`;  // specify the start page

test('Create Case', async t => {
    
    await t
        .useRole( user )
        .click(Selector('button').withText('+ Tilknyt hovedsag'))
        .typeText('#field-sbsys-id', 'xx.xx.xx-testsag')
        .typeText('#field-cpr', '000000-0000')
        .click(Selector('label').withAttribute('for', 'inputRadio1'))
        .click('#selectField4')
        .click(Selector('#selectField4 option').withText('Baltorp'))
        .click('#field-indsatstrappe')
        .click(Selector('#field-indsatstrappe option').withText('Trin 3 - Hjemmebaserede indsatser'))
        .click('#field-skaleringstrappe')
        .click(Selector('#field-skaleringstrappe option').withText('10'))
        .click(Selector('input').withAttribute('type', 'submit'))
        .expect(Selector('.case-header h1').innerText).contains('xx.xx.xx-testsag')

})
