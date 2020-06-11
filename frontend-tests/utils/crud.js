import { Selector } from 'testcafe'
import { axe } from '../utils/axe.js'
import { useSelectBox } from './utils.js'

async function editActivity(t, act_data) {
    await activityFormInput(t, act_data)
}

async function createActivity(t, act_data) {
    await t.click(Selector('.activities-create-btn'))
    await activityFormInput(t, act_data)
}

async function activityFormInput(t, act_data) {

    /*
    Example act_data
    act_data: {
        status: 'DRAFT',
        fictive: false,
        details__name: null,
        note: 'This is a nice little note',
        payment_type: 'RUNNING_PAYMENT',
        start_date: null,
        end_date: null,
        payment_frequency: 'MONTHLY',
        pay_day_of_month: 1,
        amount: '100.00',
        recipient_type: 'COMPANY',
        recipient_id: '12341234',
        recipient_name: 'CompanyName & Co',
        payment_method: 'INVOICE'
    }
    */

    if (act_data.status === 'EXPECTED') {
        await t.click(Selector('label').withAttribute('for', 'status'))
    }
    if (act_data.fictive) {
        await t.click(Selector('label').withAttribute('for', 'pay-fictional'))
    }
    if (act_data.details__name) {
        await useSelectBox(t, '#fieldSelectAct', act_data.details__name)
    } else {
        await useSelectBox(t, '#fieldSelectAct', null)
    }
    if (act_data.note) {
        await t.typeText('#note', act_data.note, {replace: true})
    }
    if (act_data.payment_type === 'RUNNING_PAYMENT') {
        await t.click(Selector('label').withAttribute('for', 'pay-type-running'))
        if (act_data.start_date) {
            await t.typeText('#pay-date-start', act_data.start_date, {replace: true})
        }
        if (act_data.end_date) {
            await t.typeText('#pay-date-end', act_data.end_date, {replace: true})
        }
    } else {
        await t.click(Selector('label').withAttribute('for', 'pay-type-single'))
        if (act_data.start_date) {
            await t.typeText('#pay-date-single', act_data.start_date, {replace: true})
        }
    }
    
    switch(act_data.payment_frequency) {
        case 'MONTHLY':
            await t.click(Selector('label').withAttribute('for', 'pay_freq_month'))
            if (act_data.pay_day_of_month) {
                await useSelectBox(t, '#pay_day_of_month', act_data.pay_day_of_month)
            }
            break
        case 'BIWEEKLY':
            await t.click(Selector('label').withAttribute('for', 'pay_freq_biweek'))
            break
        case 'WEEKLY':
            await t.click(Selector('label').withAttribute('for', 'pay_freq_week'))
            break
        case 'DAILY':
            await t.click(Selector('label').withAttribute('for', 'pay_freq_day'))
            break
        default:
    }
    
    // TODO: INSERT CHOICE OF PAYMENT COST TYPE ("RATE", "FIXED", "PER_UNIT")
    await t.click(Selector('label').withAttribute('for', 'pay-cost-type-fixed'))
    
    if (act_data.amount) {
        await t.typeText('#field-amount-1', act_data.amount, {replace: true})
    }
    switch(act_data.recipient_type) {
        // TODO:  
        case 'COMPANY':
            await t.click(Selector('label').withAttribute('for', 'pay-receiver-type-company'))
            await useSelectBox(t, '#field-select-company', act_data.recipient_name)
            break
        case 'PERSON':
            await t
                .click(Selector('label').withAttribute('for', 'pay-receiver-type-person'))
                .typeText('#field-cpr', act_data.recipient_id)
            switch(act_data.payment_method) {
                case 'SD':
                    await t
                        .click(Selector('label').withAttribute('for', 'pay-method-sd'))
                        // TODO: Hardcoding payment method details for now
                        .click(Selector('label').withAttribute('for', 'pay-method-detail-1'))
                    break
                case 'CASH':
                    await t.click(Selector('label').withAttribute('for', 'pay-method-cash'))
                    break
                default:
            }
            break
        case 'INTERNAL':
            // TODO: No internal reciever select box present as of yet
            await t.click(Selector('label').withAttribute('for', 'pay-receiver-type-internal'))
            await useSelectBox(t, '#field-select-internal', act_data.recipient_name)    
            await t.typeText('#pay-receiver-id', act_data.recipient_id)
            break
        default:
    }

    await axe(t)

    await t
        .click('#activity-submit')
        .expect(Selector('h1').withText('Bevillingsskrivelse')).ok()
}

async function createCase(t, case_data) {

    await t
        .click(Selector('button').withText('+ Tilknyt hovedsag'))
        .typeText('#field-sbsys-id', case_data.name)
        .typeText('#field-cpr', '000000-0000')
        .click('#selectTargetGroup')
        .click(Selector('#selectTargetGroup option').withText('Familieafdelingen'))
        .click('#selectDistrict')
        .click(Selector('#selectDistrict option').withText('Baltorp'))
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
    createCase,
    editActivity
}