import { Selector } from 'testcafe'
import baseurl from './url.js'

async function navToCase(t, case_sbsys_id) {
    await t
        .navigateTo(`${baseurl}/#/cases`)
        .typeText(Selector('#field-sbsysid'), case_sbsys_id, {replace: true})
        .wait(500)
        .click(Selector(`.datagrid-action[title="${case_sbsys_id}"] > a`))
        .expect(Selector('h1').withText(case_sbsys_id).exists).ok()
}

async function navToAppropriation(t, appr_sbsys_id) {
    await t
        .navigateTo(`${baseurl}/#/appropriations`)
        .typeText(Selector('#field-sbsysid'), appr_sbsys_id, {replace: true})
        .wait(500)
        .click(Selector(`.datagrid-action[title="${appr_sbsys_id}"] > a`))
        .expect(Selector('dd').withText(appr_sbsys_id).exists).ok()
}

async function navToActivity(t, act_id) {
    await t
        .navigateTo(`${baseurl}/#/activity/${act_id}/`)
        .expect(Selector('h1').withText('Udgift til').exists).ok()
}

export {
    navToCase,
    navToAppropriation,
    navToActivity
}