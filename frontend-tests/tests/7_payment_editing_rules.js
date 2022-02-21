// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { familieraadgiver, regelmotor } from '../utils/logins.js'
import baseurl from '../utils/url.js'
import { createDate } from '../utils/utils.js'
import { approveActivities } from '../utils/crud.js'
import checkConsole from '../utils/console.js'
import { navToActivity } from '../utils/navigation.js'
import { appr7, act71, act72, act73, act74 } from '../testdata.js'

fixture('Check payment editing rules')
    .page(baseurl)
    .afterEach(() => checkConsole())

/*
    Rules to test: (See https://redmine.magenta-aps.dk/issues/38276)
    Betaling 
        Kan oprettes manuelt af alle brugere
            *hvis* den tilhører en ydelse med individuel betaling
            *indtil* relateret ydelse er bevilget

    Betaling -> Planlagt beløb
        Kan ændres af alle brugere
            *hvis* den tilhører en ydelse med individuel betaling
            *indtil* relateret ydelse er bevilget

    Betaling -> Planlagt betalingsdato
        Kan ændres af alle brugere
            *hvis* den tilhører en ydelse med individuel betaling
            *indtil* relateret ydelse er bevilget
*/

test
    .before(async t => {
        await t.useRole(familieraadgiver)
    })('Check that normal user can create new payments', async t => {

    await navToActivity(t, act71.id)

    await t
        // Check that this user can create new payments on an activity that has individual payment plan
        .click('.payment-create-btn')
        .typeText('#field-payment-planned-amount', '145,95')
        .typeText('#field-payment-planned-date', createDate(4))
        .click('#submit-planned-payment-btn')
        .expect(Selector('.payment_schedule_list').exists).ok()
        // Check that this user can edit planned payments
        .click(Selector('button').withText('#').nth(0))
        .typeText('#field-planned-amount', '140', {replace: true})
        .typeText('#field-planned-date', createDate(5), {replace: true})
        .click(Selector('input').withAttribute('value', 'Opdatér'))
        .expect(Selector('.msg').withText('Betaling opdateret').exists).ok()
        // Check that this user can't create new payments on an activity that hasn't individual payment plan
        .click('button.modal-cancel-btn')
    
    await navToActivity(t, act72.id)
        
    await t.expect(Selector('.payment-create-btn').exists).notOk()
})

test
    .before(async t => {
        await t.useRole(regelmotor)
    })('Check that improved user can create new payments', async t => {

    await navToActivity(t, act71.id)

    await t
        
        // Check that this user can create new payments on an activity that has individual payment plan
        .click('.payment-create-btn')
        .typeText('#field-payment-planned-amount', '150')
        .typeText('#field-payment-planned-date', createDate(6))
        .click('#submit-planned-payment-btn')
        .expect(Selector('.payment_schedule_list').exists).ok()

        // Check that this user can edit payments
        .click(Selector('button').withText('#').nth(0))
        .typeText('#field-planned-amount', '140', {replace: true})
        .typeText('#field-planned-date', createDate(5), {replace: true})
        .click(Selector('input').withAttribute('value', 'Opdatér'))
        .expect(Selector('.msg').withText('Betaling opdateret').exists).ok()
        
        // Check that this user can't create new payments on an activity that hasn't individual payment plan
        .click('button.modal-cancel-btn')
    
    await navToActivity(t, act72.id)

    await t
        .expect(Selector('.payment-create-btn').exists).notOk()

        // Check that this user cannot edit payments
        .click(Selector('button').withText('#').nth(0))
        .expect(Selector('dt').withText('Beløb, planlagt').exists).ok()
        .click('.modal-cancel-btn')

        // Check that this user can't create new payments on any activity when activities have been granted
        .click(Selector('a').withText(appr7.sbsys_id))
        
    await approveActivities(t)

    await navToActivity(t, act71.id)

    await t.expect(Selector('.payment-create-btn').exists).notOk()
    
    await navToActivity(t, act72.id)

    await t.expect(Selector('.payment-create-btn').exists).notOk()
})

test
    .before(async t => {
        await t.useRole(familieraadgiver)
    })('Check that normal user cannot create new payments after grant', async t => {

        await navToActivity(t, act71.id)

    await t
        .expect(Selector('.payment-create-btn').exists).notOk()
        
        // Check that this user cannot edit payments anymore
        .click(Selector('button').withText('#').nth(0))
        .expect(Selector('dt').withText('Beløb, planlagt').exists).ok()
        .click('button.modal-cancel-btn')

    await navToActivity(t, act72.id)    

    await t
        .expect(Selector('.payment-create-btn').exists).notOk()
        
        // Check that this user cannot edit payments
        .click(Selector('button').withText('#').nth(0))
        .expect(Selector('dt').withText('Beløb, planlagt').exists).ok()
})

/*
    Rules to test:
    Betaling -> Betalt beløb
        Kan ændres af alle brugere,
            *hvis* den tilhører en ydelse med fakturabetaling eller intern betaling
            *indtil* første gang beløb rettes (meldt betalt, som nu)
        Kan ændres af admin/regelmotor
            for alle ydelser
            på alle tidspunkter
            *skal advares,* hvis ændring sker på en betaling
                *hvis* den tilhører en ydelse med SD-løn eller kontant udbetaling
                og *hvis* dags dato er op til 2 betalingsdage før planlagt betalingsdato (beløb vil blive overskrevet)

    Betaling -> Faktisk betalingsdato
        Kan ændres af alle brugere
            *hvis* den tilhører en ydelse med fakturabetaling eller intern betaling
            *indtil* første gang beløb rettes (meldt betalt, som nu)
        Kan ændres af admin/regelmotor
            for alle ydelser
            på alle tidspunkter
            *skal advares,* hvis ændring sker på en betaling
                *hvis* den tilhører en ydelse med SD-løn eller kontant udbetaling
                og *hvis* dags dato er op til 2 betalingsdage før planlagt betalingsdato (betalingsdato vil blive overskrevet)
*/

test
    .before(async t => {
        await t.useRole(familieraadgiver)
    })('Check that normal user can register payment under certain circumstances', async t => {

    await navToActivity(t, act71.id)

    await t
        .expect(Selector('td input.field-amount').exists).ok()
        .expect(Selector('td input[type="date"]').exists).ok()

    await navToActivity(t, act72.id)

    await t
        .expect(Selector('td input.field-amount').exists).notOk()
        .expect(Selector('td input[type="date"]').exists).notOk()

    await navToActivity(t, act73.id)

    await t
        .expect(Selector('td input.field-amount').exists).notOk()
        .expect(Selector('td input[type="date"]').exists).notOk()
    
    await navToActivity(t, act74.id)

    await t
        // Select act4 start_date year for list of payments.
        .click(Selector('#field-year-picker'))
        .click(Selector('#field-year-picker')
            .find('option')
            .withText(act74.start_date.substring(0,4))
        )

        .expect(Selector('td input.field-amount').exists).ok()
        .expect(Selector('td input[type="date"]').exists).ok()
        .typeText(Selector('td input.field-amount').nth(0), '200', {replace: true})
        .typeText(Selector('td input[type="date"]').nth(0), createDate(6), {replace: true})
        .click(Selector('button').withText('Gem'))
        .expect(Selector('span.amount-paid').exists).ok()
        .expect(Selector('span.date-paid').exists).ok()
})

test
    .before(async t => {
        await t.useRole(regelmotor)
    })('Check that improved user can register payment at all times', async t => {

    await navToActivity(t, act71.id)

    await t
        .expect(Selector('td input.field-amount').exists).ok()
        .expect(Selector('td input[type="date"]').exists).ok()

    await navToActivity(t, act72.id)

    await t
        .expect(Selector('td input.field-amount').exists).ok()
        .expect(Selector('td input[type="date"]').exists).ok()

    await navToActivity(t, act73.id)

    await t
        .expect(Selector('td input.field-amount').exists).ok()
        .expect(Selector('td input[type="date"]').exists).ok()

    await navToActivity(t, act74.id)
    
    await t
        // Select act4 start_date year for list of payments.
        .click(Selector('#field-year-picker'))
        .click(Selector('#field-year-picker')
            .find('option')
            .withText(act74.start_date.substring(0,4))
        )

        .expect(Selector('td input.field-amount').exists).ok()
        .expect(Selector('td input[type="date"]').exists).ok()
        .typeText(Selector('td input.field-amount').nth(0), '200', {replace: true})
        .typeText(Selector('td input[type="date"]').nth(0), createDate(6), {replace: true})
        .click(Selector('button').withText('Gem'))
        .expect(Selector('span.amount-paid').exists).notOk()
        .expect(Selector('span.date-paid').exists).notOk()

        // Check that we get a warning if trying to set paid date in the near future

    await navToActivity(t, act72.id)
    
    await t
        .typeText(Selector('td input[type="date"]').nth(0), createDate(1), {replace: true})
        .expect(Selector('.popover').exists).ok()
    
    await navToActivity(t, act73.id)

    await t
        .typeText(Selector('td input[type="date"]').nth(0), createDate(1), {replace: true})
        .expect(Selector('.popover').exists).ok()
})