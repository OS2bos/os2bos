import { epoch2DateStr } from '../filters/Date.js'

function sanitizeActivity(activity, request_mode) {
    
    let new_act = activity

    switch(new_act.payment_plan.payment_cost_type) {
        case 'PER_UNIT':
            new_act.payment_plan.payment_amount = null // per_unit_price.amount is used instead
            new_act.payment_plan.payment_rate = null // rate does not apply
            if (new_act.status === 'EXPECTED' && request_mode === 'post') { // When posting an expected activity, backend only accepts unchanged price_per_unit if amount is set to the same as current_amount
                if (!new_act.payment_plan.price_per_unit.amount) {
                    new_act.payment_plan.price_per_unit.amount = new_act.payment_plan.price_per_unit.current_amount
                }
                if (!new_act.payment_plan.price_per_unit.start_date) {
                    new_act.payment_plan.price_per_unit.start_date = epoch2DateStr(new Date())
                }
            }

        break
        case 'GLOBAL_RATE':
            new_act.payment_plan.payment_amount = null // amount does not apply
            new_act.payment_plan.price_per_unit = null // price per unit does not apply
        break
        default:
            // Assuming default is FIXED cost type
            new_act.payment_plan.payment_rate = null // rate does not apply
            new_act.payment_plan.price_per_unit = null // price per unit does not apply
            new_act.payment_plan.payment_units = null // units do not apply
    }

    delete new_act.monthly_payment_plan // no need to supply the monthly payment plan. DB already knows it
    delete new_act.payment_plan.payments // no need to supply the payments. DB already knows it

    return new_act
}

export {
    sanitizeActivity
}