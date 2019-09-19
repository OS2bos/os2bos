import { Selector } from 'testcafe'

async function createActivity(t, act_data) {

    if (act_data.expected_type === 'adjustment') {
        await t.click(Selector('.act-edit-btn'))
    } else {
        await t.click(Selector('.activities-create-btn'))
    }

    if (act_data.expected_type === 'expectation') {
        await t.click(Selector('label').withAttribute('for', 'field-status-expected'))
    }

    await t
        .click('#fieldSelectAct')
        .click(Selector('#fieldSelectAct option').nth(act_data.type))
        .typeText('#field-startdate', act_data.start)
        .typeText('#field-enddate', act_data.end)
        .typeText('#field-text', act_data.note)
        .click('#pay-type-2')
        .typeText('#field-amount-1', act_data.amount)
        .click('#pay-freq')
        .click(Selector('#pay-freq option').withAttribute('value', 'MONTHLY'))
        .click('#pay-day-of-month')
        .click(Selector('#pay-day-of-month option').nth(1))
        .click('#field-payee')
        .click(Selector('#field-payee option').nth(1))
        .typeText('#field-payee-id', act_data.payee_id)
        .typeText('#field-payee-name', act_data.payee_name)
        .click('#field-pay-method')
        .click(Selector('#field-pay-method option').nth(0))
        .click(Selector('input').withAttribute('type', 'submit'))
}

export { createActivity }