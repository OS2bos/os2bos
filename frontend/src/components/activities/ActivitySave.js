function sanitizeActivity(activity) {
    
    let new_act = activity

    if (new_act.payment_plan.payment_type === 'ONE_TIME_PAYMENT') {
        new_act.end_date = new_act.start_date // One time payments have the end date set to equal the start date
    }

    switch(new_act.payment_plan.payment_cost_type) {
        case 'PER_UNIT':
            new_act.payment_plan.payment_amount = null // per_unit_price.amount is used instead
            new_act.payment_plan.payment_rate = null // rate does not apply
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

    return new_act
}

export {
    sanitizeActivity
}