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
        payment_date: null,
        start_date: null,
        end_date: null,
        payment_frequency: 'MONTHLY',
        pay_day_of_month: '1',
        payment_cost_type: 'FIXED', // or 'GLOBAL_RATE'|'PER_UNIT'
        payment_amount: '100.00',
        payment_units: '2.5',
        recipient_type: 'COMPANY',
        recipient_id: '12341234',
        recipient_name: 'CompanyName & Co',
        payment_method: 'INVOICE',
        price_amount: '100.00', // if payment_cost_type === 'PER_UNIT'
        price_start_date: '2020-01-31', // if payment_cost_type === 'PER_UNIT'
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
    }
    if (act_data.note) {
        await t.typeText('#note', act_data.note, {replace: true})
    }

    switch(act_data.payment_type) {
        case 'RUNNING_PAYMENT':
            await t.click(Selector('label').withAttribute('for', 'pay-type-running'))
            break
        case 'INDIVIDUAL_PAYMENT':
            await t.click(Selector('label').withAttribute('for', 'pay-type-individual'))
            break
        case 'ONE_TIME_PAYMENT':
            await t.click(Selector('label').withAttribute('for', 'pay-type-single'))
            break
        default: 
    }

    if (act_data.start_date) {
        await t.typeText('#pay-date-start', act_data.start_date, {replace: true})
    }
    if (act_data.end_date) {
        await t.typeText('#pay-date-end', act_data.end_date, {replace: true})
    }
    if (act_data.payment_date) {
        await t.typeText('#pay-date-single', act_data.payment_date, {replace: true})
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
    
    switch(act_data.payment_cost_type) {
        case 'GLOBAL_RATE':
            await t.click(Selector('label').withAttribute('for', 'pay-cost-type-rate'))
            await useSelectBox(t, '#field-rates')
            await t.typeText('#pay-units', act_data.payment_units, {replace: true})
            break
        case 'PER_UNIT':
            await t
                .click(Selector('label').withAttribute('for', 'pay-cost-type-per-unit'))
                .typeText('#pay-cost-pr-unit', act_data.price_amount, {replace: true})
                .typeText('#pay-units', act_data.payment_units, {replace: true})
                if (act_data.price_start_date === null) {
                    await t.typeText('#pay-cost-exec-date', act_data.price_start_date, {replace: true})
                }
            break
        case 'FIXED':
            await t.click(Selector('label').withAttribute('for', 'pay-cost-type-fixed'))
            await t.typeText('#field-amount-1', act_data.payment_amount, {replace: true})
            break
        default:
    }
    
    switch(act_data.recipient_type) {
        case 'COMPANY':
            await t.click(Selector('label').withAttribute('for', 'pay-receiver-type-company'))
            if (act_data.recipient_id) {
                await t
                    .typeText('#cvr-search-input', act_data.recipient_id)
                    .click(Selector('.cvr-search-result .cvr-select-btn').withText(act_data.recipient_id))
            } else {
                await t
                    .typeText('#cvr-search-input', 'Magenta')
                    .click(Selector('.cvr-search-result .cvr-select-btn').nth(0))
            }
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
        .expect(Selector('h1').withText('Udgift til').exists).ok()
        .click(Selector('a').withText('Bevillingsskrivelse'))
        .expect(Selector('h1').withText('Bevillingsskrivelse').exists).ok()
}

async function createCase(t, case_data) {

    /*
    Example case_data
    case_data: {
        name: 'xx.xx.xx',
        effort_step: 'Trin 3',
        scaling_step: '5',
        target_group: 'Familieafdelingen',
        district: 'Baltorp',
        cpr: '0000000000'
    }
    */
    
    await t
        .click(Selector('button').withText('+ Tilknyt hovedsag'))
        .typeText('#field-sbsys-id', case_data.name)
    
    if (case_data.cpr) {
        await t.typeText('#field-cpr', case_data.cpr)
    } else {
        await t.typeText('#field-cpr', '000000-0000')
    }

    await useSelectBox(t, '#selectTargetGroup', case_data.target_group)
    if (case_data.district) {
        await useSelectBox(t, '#selectDistrict', case_data.district)
    }
    if (case_data.effort_step) {
        await useSelectBox(t, '#field-indsatstrappe', case_data.effort_step)
    }
    if (case_data.scaling_step) {
        await useSelectBox(t, '#field-skaleringstrappe', case_data.scaling_step)
    }

    await t.click(Selector('input').withAttribute('type', 'submit'))
}

async function createAppropriation(t, appr_data) {

    /*
    Example appr_data
    appr_data: {
        name: 'xx.xx.xx-yy',
        section: 'SEL-109 Botilbud'        
    }
    */

    await t
        .click(Selector('.appropriation-create-btn'))
        .typeText('#field-sbsysid', appr_data.name)
    
    await useSelectBox(t, '#field-lawref', appr_data.section)

    await t.click(Selector('input').withAttribute('type', 'submit'))
}

async function approveActivities(t) {
    await t
        .click(Selector('label').withAttribute("for", "check-all"))
        .click(Selector('button').withText('Godkend valgte'))
        .click(Selector('label').withAttribute('for','radio-btn-1'))
        .click('button[type="submit"]')
}

async function createPayment(t, payment_data) {

    await t
        .click(Selector('.payment-create-btn'))
        .typeText('#field-payment-planned-amount', payment_data.amount, {replace: true})
        .typeText('#field-payment-planned-date', payment_data.date, {replace: true})
        .click(Selector('#submit-planned-payment-btn'))
        .expect(Selector('h2').withText('Opret ny betaling').exists).notOk()
}

export {
    approveActivities,
    createActivity,
    createAppropriation,
    createCase,
    editActivity,
    createPayment
}