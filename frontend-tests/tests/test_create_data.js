// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { loginAsUngeraadgiver } from '../utils/logins.js'

const testdata = {
    case1: {
        name: 'xx.xx.xx-testsag'
    },
    appr1: {
        name: 'xx.xx.xx-yy-testbevilling',
        section: 'SEL-109 Botilbud, kriseramte kvinder'
    }
}

fixture `Create some data`// declare the fixture
    .page `http://localhost:8080/#/my-cases/`  // specify the start page

test('Create Case', async t => {

    await loginAsUngeraadgiver(t)
    
    await t
        .navigateTo('http://localhost:8080/#/')
        .click(Selector('button').withText('+ Tilknyt hovedsag'))
        .typeText('#field-sbsys-id', testdata.case1.name)
        .typeText('#field-cpr', '000000-0000')
        .click(Selector('label').withAttribute('for', 'inputRadio1'))
        .click('#selectField4')
        .click(Selector('#selectField4 option').withText('Baltorp'))
        .click('#field-indsatstrappe')
        .click(Selector('#field-indsatstrappe option').withText('Trin 3 - Hjemmebaserede indsatser'))
        .click('#field-skaleringstrappe')
        .click(Selector('#field-skaleringstrappe option').withText('10'))
        .click(Selector('input').withAttribute('type', 'submit'))
        .navigateTo('http://localhost:8080/#/')
        .expect(Selector('.cases table tr:first-child td a').innerText).contains(testdata.case1.name)
})

test('Create Appropriation', async t => {

    await loginAsUngeraadgiver(t)

    await t
        .navigateTo('http://localhost:8080/#/')
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('.appropriation-create-btn'))
        .typeText('#field-sbsysid', testdata.appr1.name)
        .click('#field-lawref')
        .click(Selector('#field-lawref option').withText(testdata.appr1.section))
        .click(Selector('input').withAttribute('type', 'submit'))
        .navigateTo('http://localhost:8080/#/')
        .click(Selector('a').withText(testdata.case1.name))
        .expect(Selector('.appropriation-list tr:first-child td a').innerText).contains(testdata.appr1.name)
})

test('Create Activity', async t => {
    
    await loginAsUngeraadgiver(t)

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))
        .click(Selector('.activities-create-btn'))
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
