import { epoch2DateStr } from '../filters/Date.js'
import PermissionLogic from '../mixins/PermissionLogic.js'
import store from '../../store.js'

function sanitizeActivity(activity, request_mode) {
    
    const today = epoch2DateStr(new Date()),
        in_one_week = epoch2DateStr(new Date().setDate(new Date().getDate() + 7))
    
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
                    new_act.payment_plan.price_per_unit.start_date = today
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

    if (new_act.payment_plan.payment_frequency !== 'MONTHLY') {
        delete new_act.payment_plan.payment_day_of_month // Only monthly payments must supply a day of month
    }

    if (PermissionLogic.methods.is_individual_payment_type(new_act.payment_plan) && request_mode === 'post') {
        new_act.start_date = in_one_week // Posted activity MUST have a start date and it must be somewhere in the next few days depending on weekends and holidays. Since we don't know about specific holidays, we set it at about a week from now.
        new_act.payment_plan.payment_cost_type = null // Individual payment plan does not need cost type, but it must be null so backend does not assign 'FIXED' as default
        delete new_act.payment_plan.payment_units // Individual payment plan must not have units
        delete new_act.payment_plan.payment_rate // Individual payment plan must not have rate
        delete new_act.payment_plan.price_per_unit // Individual payment plan must not have price pr unit
        delete new_act.payment_plan.payment_amount  // Individual payment plan must not have amount
        
    }

    if (PermissionLogic.methods.is_individual_payment_type(new_act.payment_plan)) {
        delete new_act.payment_plan.payment_day_of_month // Individual payment plan can't have payment day of month

        if (new_act.payment_plan.recipient_type === 'INTERNAL' && !new_act.payment_plan.recipient_id) { // If no recipient ID is supplied, make one up using ID derived from recipient's name
            const internal_recipients = store.getters.getInternalPaymentRecipients
            const internal_recipient = internal_recipients.find(function(recip) {
                return recip.name === new_act.payment_plan.recipient_name
            })
            new_act.payment_plan.recipient_id = internal_recipient.id
        }
    }

    delete new_act.monthly_payment_plan // no need to supply the monthly payment plan. DB already knows it
    delete new_act.payment_plan.payments // no need to supply the payments. DB already knows it

    return new_act
}

export {
    sanitizeActivity
}