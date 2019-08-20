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

test('Create Appropriation', async t => {
    
    await t
        .navigateTo('localhost:8080/#/my-cases/')
        .useRole( user )
        .click(Selector('a').withText('xx.xx.xx-testsag'))
        .click(Selector('.appropriation-create-btn'))
        .typeText('#field-sbsysid', 'xx.xx.xx-yy-testbevilling')
        .click('#field-lawref')
        .click(Selector('#field-lawref option').nth(1))
        .click(Selector('input').withAttribute('type', 'submit'))
        .expect(Selector('.appropriation-header h1').innerText).contains('Bevillingsskrivelse')

})

test('Create Activity', async t => {
    
    await t
        .navigateTo('localhost:8080/#/my-cases/')
        .useRole( user )
        .click(Selector('a').withText('xx.xx.xx-testsag'))
        .click(Selector('a').withText('xx.xx.xx-yy-testbevilling'))
        .click(Selector('.activities-create-btn'))
        .click(Selector('label').withAttribute('for', 'field-type-main'))
        .click('#fieldSelectAct')
        .click(Selector('#fieldSelectAct option').nth(1))
        .typeText('#field-startdate', '2019-08-21')
        
        /*
        .typeText('#field-sbsysid', 'xx.xx.xx-yy-testbevilling')
        .click('#field-lawref')
        .click(Selector('#field-lawref option').nth(1))
        .click(Selector('input').withAttribute('type', 'submit'))
        .expect(Selector('.appropriation-header h1').innerText).contains('Bevillingsskrivelse')
        */
        
        

})
