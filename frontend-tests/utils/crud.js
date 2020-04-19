import { Selector } from 'testcafe'
import { axe, axeOptions } from '../utils/axe.js'

async function createActivity(t, act_data) {

    if (act_data.expected_type === 'adjustment') {
        await t.click(Selector('.act-edit-btn'))
    } else {
        await t.click(Selector('.activities-create-btn'))
    }

    if (act_data.expected_type === 'expectation') {
        await t.click(Selector('label').withAttribute('for', 'field-status-expected'))
    }

    await axe(t, null, axeOptions)

    if (act_data.type === 1) {
        await t
            .click('#fieldSelectAct')
            .click(Selector('#fieldSelectAct option').nth(act_data.type))
    }

    await t
        .typeText('#field-startdate', act_data.start)

    if (act_data.end) {
        await t.typeText('#field-enddate', act_data.end)
    }
    if (act_data.note) {
        await t.typeText('#field-text', act_data.note)
    }

    await t.click('#pay-type-2')

    if (act_data.amount) {
        await t.typeText('#field-amount-1', act_data.amount, {replace: true})
    }

    await t
        .click('#pay-freq')
        .click(Selector('#pay-freq option').withAttribute('value', 'MONTHLY'))
        .click('#pay-day-of-month')
        .click(Selector('#pay-day-of-month option').nth(1))
        .click('#field-payee')
        .click(Selector('#field-payee option').nth(1))

    if (act_data.payee_id) {
        await t.typeText('#field-payee-id', act_data.payee_id)
    }
    if (act_data.payee_name) {
        await t.typeText('#field-payee-name', act_data.payee_name)
    }

    await t
        .click(Selector('input').withAttribute('type', 'submit'))
        .expect(Selector('h1').withText('Bevillingsskrivelse')).ok()
}

async function createCase(t, case_data) {

    await t
        .click(Selector('button').withText('+ Tilknyt hovedsag'))
        .typeText('#field-sbsys-id', case_data.name)
        .typeText('#field-cpr', '000000-0000')
        .click(Selector('label').withAttribute('for', 'inputRadio1'))
        .click('#selectField4')
        .click(Selector('#selectField4 option').withText('Baltorp'))
        .click('#field-indsatstrappe')
        .click(Selector('#field-indsatstrappe option').withText('Trin 3: Hjemmebaserede indsatser'))
        .click('#field-skaleringstrappe')
        .click(Selector('#field-skaleringstrappe option').withText('5'))
        .click(Selector('input').withAttribute('type', 'submit'))
}

async function createAppropriation(t, appr_data) {

    await t
        .click(Selector('.appropriation-create-btn'))
        .typeText('#field-sbsysid', appr_data.name)
        .click('#field-lawref')
        .click(Selector('#field-lawref option').nth(1))
        .click(Selector('input').withAttribute('type', 'submit'))
}

async function approveActivities(t) {
    
    await t
        .click('#check-all')
        .click(Selector('button').withText('Godkend valgte'))
        .click(Selector('label').withAttribute('for','radio-btn-1'))
        .click('button[type="submit"]')
}

export {
    approveActivities,
    createActivity,
    createAppropriation,
    createCase
}