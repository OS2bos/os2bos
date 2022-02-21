// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector, ClientFunction } from 'testcafe'
import { familieraadgiver, admin } from '../utils/logins.js'
import baseurl from '../utils/url.js'
import { useSelectBox } from '../utils/utils.js'
import checkConsole from '../utils/console.js'
import { case81, case82, appr81, appr82 } from '../testdata.js'

const getLocation = ClientFunction(() => document.location.href)


fixture('Check search filter defaults')
    .afterEach(() => checkConsole())

/*
    Rules to test: 
    
    References
    https://redmine.magenta-aps.dk/issues/39356
    https://redmine.magenta-aps.dk/issues/40312
    https://redmine.magenta-aps.dk/issues/40341
    https://redmine.magenta-aps.dk/issues/43490
*/

// When loading cases page with no query params, 
// default case worker filter should default to current user
// When setting case worker filter, 
// both URL param, results, and filter setting should update
test
.before(async t => {
    await t.useRole(admin)
})
.page(`${ baseurl }/#/cases`)
('Test default filtering, filter change, and reset on cases list', async t => {

    // Set current user as default case worker when no params present
    await t
        .expect(getLocation()).contains('case_worker=2')
        .expect(Selector('select#field-case-worker option').withText('IT Guy (admin)').selected).ok()
        .expect(Selector('a').withText(case81.sbsys_id).exists).ok()
        .expect(Selector('a').withText(case82.sbsys_id).exists).notOk()

    // Update page, when another case worker is selected
    await useSelectBox(t, '#field-case-worker', 'Familie Raadgiver (familieraadgiver)')

    await t
        .expect(getLocation()).contains('case_worker=3')
        .expect(Selector('select#field-case-worker option').withText('Familie Raadgiver (familieraadgiver)').selected).ok()
        .expect(Selector('a').withText(case82.sbsys_id).exists).ok()
        .expect(Selector('a').withText(case81.sbsys_id).exists).notOk()

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
        .expect(Selector('a').withText(case81.sbsys_id).exists).notOk()
        .expect(Selector('a').withText(case82.sbsys_id).exists).ok()

    // Update page, when filters are reset
    await t
        .click('button.filter-reset')
        .expect(getLocation()).contains('case_worker=2')
        .expect(Selector('select#field-case-worker option').withText('IT Guy (admin)').selected).ok()
        .expect(Selector('a').withText(case81.sbsys_id).exists).ok()
        .expect(Selector('a').withText(case82.sbsys_id).exists).notOk()

})

// When loading appropriation page with no query params, 
// default case worker filter should default to current user
// When setting case worker filter, 
// both URL param, results, and filter setting should update
test
.before(async t => {
    await t.useRole(admin)
})
.page(`${ baseurl }/#/appropriations`)
('Test default filtering, filter change, and reset on appropriation list', async t => {

    // Set current user as default case worker when no params present
    await t
        .expect(getLocation()).contains('case__case_worker=2')
        .expect(Selector('select#field-case-worker option').withText('IT Guy (admin)').selected).ok()
        .expect(Selector('a').withText(appr81.sbsys_id).exists).ok()
        .expect(Selector('a').withText(appr82.sbsys_id).exists).notOk()
    
    // Update page, when another case worker is selected
    await useSelectBox(t, '#field-case-worker', 'Familie Raadgiver (familieraadgiver)')

    await t
        .expect(getLocation()).contains('case__case_worker=3')
        .expect(Selector('select#field-case-worker option').withText('Familie Raadgiver (familieraadgiver)').selected).ok()
        .expect(Selector('a').withText(appr82.sbsys_id).exists).ok()
        .expect(Selector('a').withText(appr81.sbsys_id).exists).notOk()

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
        .expect(Selector('a').withText(appr81.sbsys_id).exists).notOk()
        .expect(Selector('a').withText(appr82.sbsys_id).exists).ok()
    
    // Update page, when filters are reset
    await t
        .click('button.filter-reset')
        .expect(getLocation()).contains('case__case_worker=2')
        .expect(Selector('select#field-case-worker option').withText('IT Guy (admin)').selected).ok()
        .expect(Selector('a').withText(appr81.sbsys_id).exists).ok()
        .expect(Selector('a').withText(appr82.sbsys_id).exists).notOk()
})

// When loading cases page with query params, 
// filters should be applied based on params
test
.before(async t => {
    await t.useRole(admin)
})
.page(`${ baseurl }/#/cases?case_worker__team=3&case_worker=3`)
('When navigating cases with URL params, set filters and lists accordingly', async t => {

    await t
        .expect(getLocation()).contains('case_worker=3')
        .expect(Selector('select#field-case-worker option').withText('Familie Raadgiver (familieraadgiver)').selected).ok()
        .expect(Selector('a').withText(case82.sbsys_id).exists).ok()
        .expect(Selector('a').withText(case81.sbsys_id).exists).notOk()
})

// When loading appropriation page with query params,
// filters should be applied based on params
test
.before(async t => {
    await t.useRole(admin)
})
.page(`${ baseurl }/#/appropriations?case__case_worker__team=3&case__case_worker=3`)
('When navigating appropriations with URL params, set filters and lists accordingly', async t => {

    await t
        .expect(getLocation()).contains('case__case_worker=3')
        .expect(Selector('select#field-case-worker option').withText('Familie Raadgiver (familieraadgiver)').selected).ok()
        .expect(Selector('a').withText(appr82.sbsys_id).exists).ok()
        .expect(Selector('a').withText(appr81.sbsys_id).exists).notOk()
})

// When loading cases page with query params and no case worker, 
// filters should be applied based on params only
test
.before(async t => {
    await t.useRole(admin)
})
.page(`${ baseurl }/#/cases?case_worker__team=2`)
('Do not set default case worker when navigating cases with URL params', async t => {

    await t
        .expect(getLocation()).contains('case_worker__team=2')
        .expect(getLocation()).notContains('case_worker=2')
        .expect(Selector('select#field-case-worker option').withText('---').selected).ok()
        .expect(Selector('p').withText('Kan ikke finde nogen resultater, der matcher de valgte kriterier').exists).ok()
})

// When loading appropriations page with query params and no case worker, 
// filters should be applied based on params only
test
.before(async t => {
    await t.useRole(admin)
})
.page(`${ baseurl }/#/appropriations?case__case_worker__team=2`)
('Do not set default case worker when navigating appropriations with URL params', async t => {

    await t
        .expect(getLocation()).contains('case__case_worker__team=2')
        .expect(getLocation()).notContains('case__case_worker=2')
        .expect(Selector('select#field-case-worker option').withText('---').selected).ok()
        .expect(Selector('p').withText('Kan ikke finde nogen resultater, der matcher de valgte kriterier').exists).ok()
})

// https://redmine.magenta-aps.dk/issues/43490
// Appropriation search filter "Foranstaltningssag" should search for an appropriation's SBSYS_ID
test
.before(async t => {
    await t.useRole(familieraadgiver)
})
.page(`${ baseurl }/#/appropriations`)
('Test appropriation search filter', async t => {

    await t
        .expect(Selector('.datagrid tr').count).gt(2)
        .typeText('#field-sbsysid', appr82.sbsys_id, {replace: true})
        .expect(Selector('.datagrid td a').withText(appr82.sbsys_id).exists).ok()
        .expect(Selector('.datagrid tr').count).eql(2)
})
