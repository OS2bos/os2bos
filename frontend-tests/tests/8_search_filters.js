// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector, ClientFunction } from 'testcafe'
import { login } from '../utils/logins.js'
import baseurl from '../utils/url.js'
import { randNum, useSelectBox } from '../utils/utils.js'
import { createCase, createAppropriation } from '../utils/crud.js'

const getLocation = ClientFunction(() => document.location.href),
      testdata = {
            case1: {
                name: `filtertest-${ randNum() }.${ randNum() }.${ randNum() }`,
                effort_step: '2',
                scaling_step: '4',
                target_group: 'Handicapafdelingen'
            },
            case2: {
                name: `filtertest-${ randNum() }.${ randNum() }.${ randNum() }`,
                effort_step: '3',
                scaling_step: '5',
                target_group: 'Handicapafdelingen'
            },
            appr1: {
                name: `${ randNum() }.${ randNum() }.${ randNum() }-${ randNum() }-bevilling`,
                section: 'SEL-41 Merudgifter til børn'
            },
            appr2: {
                name: `${ randNum() }.${ randNum() }.${ randNum() }-${ randNum() }-bevilling`,
                section: 'SEL-76-2 Efterværn / kontaktperson 18-22 årige'
            },
            appr3: {
                name: `${ randNum() }.${ randNum() }.${ randNum() }-${ randNum() }-bevilling`,
                section: 'SEL-76-2 Efterværn / kontaktperson 18-22 årige'
            }
        }

fixture('Check search filter defaults')

/*
    Rules to test: 
    
    References
    https://redmine.magenta-aps.dk/issues/39356
    https://redmine.magenta-aps.dk/issues/40312
    https://redmine.magenta-aps.dk/issues/40341
    https://redmine.magenta-aps.dk/issues/43490
    
*/

test.page(baseurl)
('Create data for one user', async t => {

    await login(t, 'admin', 'admin') 

    await createCase(t, testdata.case1)
    await createAppropriation(t, testdata.appr1)
        
})

test.page(baseurl)
('Create data for another user', async t => {

    await login(t, 'familieraadgiver', 'sagsbehandler') 

    await createCase(t, testdata.case2)
    await createAppropriation(t, testdata.appr2)
    await t.click(Selector('a').withText(testdata.case2.name))
    await createAppropriation(t, testdata.appr3)
        
})

// When loading cases page with no query params, 
// default case worker filter should default to current user
// When setting case worker filter, 
// both URL param, results, and filter setting should update
test.page(`${ baseurl }/#/cases`)
('Test default filtering, filter change, and reset on cases list', async t => {

    await login(t, 'admin', 'admin')

    // Set current user as default case worker when no params present
    await t
        .expect(getLocation()).contains('case_worker=2')
        .expect(Selector('select#field-case-worker option').withText('IT Guy (admin)').selected).ok()
        .expect(Selector('a').withText(testdata.case1.name).exists).ok()
        .expect(Selector('a').withText(testdata.case2.name).exists).notOk()

    // Update page, when another case worker is selected
    await useSelectBox(t, '#field-case-worker', 'Familie Raadgiver (familieraadgiver)')

    await t
        .expect(getLocation()).contains('case_worker=3')
        .expect(Selector('select#field-case-worker option').withText('Familie Raadgiver (familieraadgiver)').selected).ok()
        .expect(Selector('a').withText(testdata.case2.name).exists).ok()
        .expect(Selector('a').withText(testdata.case1.name).exists).notOk()

    // List nothing when no filter is selected
    await useSelectBox(t, '#field-case-worker', '---')
    
    await t
        .expect(getLocation()).notContains('case_worker=3')
        .expect(Selector('p').withText('Kan ikke finde nogen resultater, der matcher de valgte kriterier').exists).ok()

    // Update list when only team is selected
    await useSelectBox(t, '#field-team', 'Familierådgivning')

    await t
        .expect(getLocation()).notContains('case_worker=')
        .expect(getLocation()).contains('case_worker__team=3')
        .expect(Selector('select#field-case-worker option').withText('---').selected).ok()
        .expect(Selector('a').withText(testdata.case1.name).exists).notOk()
        .expect(Selector('a').withText(testdata.case2.name).exists).ok()

    // Update page, when filters are reset
    await t
        .click('button.filter-reset')
        .expect(getLocation()).contains('case_worker=2')
        .expect(Selector('select#field-case-worker option').withText('IT Guy (admin)').selected).ok()
        .expect(Selector('a').withText(testdata.case1.name).exists).ok()
        .expect(Selector('a').withText(testdata.case2.name).exists).notOk()

})

// When loading appropriation page with no query params, 
// default case worker filter should default to current user
// When setting case worker filter, 
// both URL param, results, and filter setting should update
test.page(`${ baseurl }/#/appropriations`)
('Test default filtering, filter change, and reset on appropriation list', async t => {

    await login(t, 'admin', 'admin') 

    // Set current user as default case worker when no params present
    await t
        .expect(getLocation()).contains('case__case_worker=2')
        .expect(Selector('select#field-case-worker option').withText('IT Guy (admin)').selected).ok()
        .expect(Selector('a').withText(testdata.appr1.name).exists).ok()
        .expect(Selector('a').withText(testdata.appr2.name).exists).notOk()
    
    // Update page, when another case worker is selected
    await useSelectBox(t, '#field-case-worker', 'Familie Raadgiver (familieraadgiver)')

    await t
        .expect(getLocation()).contains('case__case_worker=3')
        .expect(Selector('select#field-case-worker option').withText('Familie Raadgiver (familieraadgiver)').selected).ok()
        .expect(Selector('a').withText(testdata.appr2.name).exists).ok()
        .expect(Selector('a').withText(testdata.appr1.name).exists).notOk()

    // List nothing when no filter is selected
    await useSelectBox(t, '#field-case-worker', '---')
    
    await t
        .expect(getLocation()).notContains('case__case_worker=3')
        .expect(Selector('p').withText('Kan ikke finde nogen resultater, der matcher de valgte kriterier').exists).ok()
    
    // Update list when only team is selected
    await useSelectBox(t, '#field-team', 'Familierådgivning')

    await t
        .expect(getLocation()).notContains('case__case_worker=')
        .expect(getLocation()).contains('case__case_worker__team=3')
        .expect(Selector('select#field-case-worker option').withText('---').selected).ok()
        .expect(Selector('a').withText(testdata.appr1.name).exists).notOk()
        .expect(Selector('a').withText(testdata.appr2.name).exists).ok()
    
    // Update page, when filters are reset
    await t
        .click('button.filter-reset')
        .expect(getLocation()).contains('case__case_worker=2')
        .expect(Selector('select#field-case-worker option').withText('IT Guy (admin)').selected).ok()
        .expect(Selector('a').withText(testdata.appr1.name).exists).ok()
        .expect(Selector('a').withText(testdata.appr2.name).exists).notOk()
})

// When loading cases page with query params, 
// filters should be applied based on params
test.page(`${ baseurl }/#/cases?case_worker__team=3&case_worker=3`)
('When navigating cases with URL params, set filters and lists accordingly', async t => {

    await login(t, 'admin', 'admin') 

    await t
        .expect(getLocation()).contains('case_worker=3')
        .expect(Selector('select#field-case-worker option').withText('Familie Raadgiver (familieraadgiver)').selected).ok()
        .expect(Selector('a').withText(testdata.case2.name).exists).ok()
        .expect(Selector('a').withText(testdata.case1.name).exists).notOk()
})

// When loading appropriation page with query params,
// filters should be applied based on params
test.page(`${ baseurl }/#/appropriations?case__case_worker__team=3&case__case_worker=3`)
('When navigating appropriations with URL params, set filters and lists accordingly', async t => {

    await login(t, 'admin', 'admin') 

    await t
        .expect(getLocation()).contains('case__case_worker=3')
        .expect(Selector('select#field-case-worker option').withText('Familie Raadgiver (familieraadgiver)').selected).ok()
        .expect(Selector('a').withText(testdata.appr2.name).exists).ok()
        .expect(Selector('a').withText(testdata.appr1.name).exists).notOk()
})

// When loading cases page with query params and no case worker, 
// filters should be applied based on params only
test.page(`${ baseurl }/#/cases?case_worker__team=2`)
('Do not set default case worker when navigating cases with URL params', async t => {

    await login(t, 'admin', 'admin') 

    await t
        .expect(getLocation()).contains('case_worker__team=2')
        .expect(getLocation()).notContains('case_worker=2')
        .expect(Selector('select#field-case-worker option').withText('---').selected).ok()
        .expect(Selector('p').withText('Kan ikke finde nogen resultater, der matcher de valgte kriterier').exists).ok()
})

// When loading appropriations page with query params and no case worker, 
// filters should be applied based on params only
test.page(`${ baseurl }/#/appropriations?case__case_worker__team=2`)
('Do not set default case worker when navigating appropriations with URL params', async t => {

    await login(t, 'admin', 'admin') 

    await t
        .expect(getLocation()).contains('case__case_worker__team=2')
        .expect(getLocation()).notContains('case__case_worker=2')
        .expect(Selector('select#field-case-worker option').withText('---').selected).ok()
        .expect(Selector('p').withText('Kan ikke finde nogen resultater, der matcher de valgte kriterier').exists).ok()
})

// https://redmine.magenta-aps.dk/issues/43490
// Appropriation search filter "Foranstaltningssag" should search for an appropriation's SBSYS_ID
test.page(`${ baseurl }/#/appropriations`)
('Test appropriation search filter', async t => {

    await login(t, 'familieraadgiver', 'sagsbehandler')

    await t
        .expect(Selector('.datagrid tr').count).gt(2)
        .typeText('#field-sbsysid', testdata.appr2.name, {replace: true})
        .expect(Selector('.datagrid td a').withText(testdata.appr2.name).exists).ok()
        .expect(Selector('.datagrid tr').count).eql(2)
})