// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { login } from '../utils/logins.js'
import baseurl from '../utils/url.js'
import { randNum, createDate, useSelectBox } from '../utils/utils.js'
import { createCase, createAppropriation, createActivity, approveActivities } from '../utils/crud.js'

const testdata = {
        case1: {
            name: `${ randNum() }.${ randNum() }.${ randNum() }-sag`,
            effort_step: '5',
            scaling_step: '7',
            target_group: 'Handicapafdelingen'
        },
        appr1: {
            name: `${ randNum() }.${ randNum() }.${ randNum() }-${ randNum() }-bevilling`,
            section: 'SEL-52-3.5 Aflastningsordning'
        },
        act1: {
            details__name: 'Netværksplejefamilier',
            payment_type: 'INDIVIDUAL_PAYMENT',
            start_date: createDate(2),
            end_date: createDate(32),
            recipient_type: 'COMPANY'
        },
        act2: {
            details__name: 'Aktiviteter',
            payment_type: 'RUNNING_PAYMENT',
            start_date: createDate(6),
            end_date: createDate(12),
            payment_frequency: 'DAILY',
            payment_cost_type: 'FIXED',
            payment_amount: '120,95',
            recipient_type: 'PERSON',
            recipient_id: '1111112222',
            payment_method: 'SD'
        },
        act3: {
            details__name: 'Kost og logi',
            payment_type: 'ONE_TIME_PAYMENT',
            payment_date: createDate(10),
            payment_cost_type: 'GLOBAL_RATE',
            payment_units: '5.20',
            recipient_type: 'PERSON',
            recipient_id: '2222221111',
            payment_method: 'CASH'
        },
        act4: {
            details__name: 'Kørsel i egen bil',
            payment_type: 'RUNNING_PAYMENT',
            start_date: createDate(18),
            payment_frequency: 'WEEKLY',
            payment_cost_type: 'PER_UNIT',
            price_amount: '100',
            price_start_date: createDate(1),
            payment_units: '3',
            recipient_type: 'INTERNAL',
            recipient_id: '123'
        }
    }

fixture('Check payment editing rules')
    .page(baseurl)

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

test('Create data and check that normal user can create new payments', async t => {

    await login(t, 'familieraadgiver', 'sagsbehandler') 

    await createCase(t, testdata.case1)
    await createAppropriation(t, testdata.appr1)
    await createActivity(t, testdata.act1)
    await createActivity(t, testdata.act2)
    await createActivity(t, testdata.act3)
    await createActivity(t, testdata.act4)

    await t
        // Check that this user can create new payments on an activity that has individual payment plan
        .click(Selector('a').withText(testdata.act1.details__name))
        .click('.payment-create-btn')
        .typeText('#field-payment-planned-amount', '145,95')
        .typeText('#field-payment-planned-date', createDate(4))
        .click('#submit-planned-payment-btn')
        .expect(Selector('.payment_schedule_list').exists).ok()
        // Check that this user can edit payments
        .click(Selector('button').withText('Betaling').nth(0))
        .typeText('#field-planned-amount', '140', {replace: true})
        .typeText('#field-planned-date', createDate(5), {replace: true})
        .click(Selector('input').withAttribute('value', 'Opdatér'))
        .expect(Selector('.msg').withText('Betaling opdateret').exists).ok()
        // Check that this user can't create new payments on an activity that hasn't individual payment plan
        .click(Selector('a').withText(testdata.appr1.name))
        .click(Selector('a').withText(testdata.act2.details__name))
        .expect(Selector('.payment-create-btn').exists).notOk()
})

test('Check that improved user can create new payments', async t => {

    await login(t, 'regelmotor', 'regelmotor')

    await useSelectBox(t, '#field-case-worker', 'familieraadgiver)')

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))
        .click(Selector('a').withText(testdata.act1.details__name))
        
        // Check that this user can create new payments on an activity that has individual payment plan
        .click('.payment-create-btn')
        .typeText('#field-payment-planned-amount', '150')
        .typeText('#field-payment-planned-date', createDate(6))
        .click('#submit-planned-payment-btn')
        .expect(Selector('.payment_schedule_list').exists).ok()

        // Check that this user can edit payments
        .click(Selector('button').withText('Betaling').nth(0))
        .typeText('#field-planned-amount', '140', {replace: true})
        .typeText('#field-planned-date', createDate(5), {replace: true})
        .click(Selector('input').withAttribute('value', 'Opdatér'))
        .expect(Selector('.msg').withText('Betaling opdateret').exists).ok()
        
        // Check that this user can't create new payments on an activity that hasn't individual payment plan
        .click(Selector('a').withText(testdata.appr1.name))
        .click(Selector('a').withText(testdata.act2.details__name))
        .expect(Selector('.payment-create-btn').exists).notOk()

        // Check that this user cannot edit payments
        .click(Selector('button').withText('Betaling').nth(0))
        .expect(Selector('dt').withText('Beløb, planlagt').exists).ok()
        .click('.modal-cancel-btn')

        // Check that this user can't create new payments on any activity when activities have been granted
        .click(Selector('a').withText(testdata.appr1.name))
        
    await approveActivities(t)

    await t
        .click(Selector('a').withText(testdata.act1.details__name))
        .expect(Selector('.payment-create-btn').exists).notOk()
        .click(Selector('a').withText(testdata.appr1.name))
        .click(Selector('a').withText(testdata.act2.details__name))
        .expect(Selector('.payment-create-btn').exists).notOk()
})

test('Check that normal user cannot create new payments after grant', async t => {

    await login(t, 'familieraadgiver', 'sagsbehandler')

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))
        .click(Selector('a').withText(testdata.act1.details__name))
        .expect(Selector('.payment-create-btn').exists).notOk()
        
        // Check that this user cannot edit payments anymore
        .click(Selector('button').withText('Betaling').nth(0))
        .expect(Selector('dt').withText('Beløb, planlagt').exists).ok()
        .click(Selector('button').withText('Luk'))

        .click(Selector('a').withText(testdata.appr1.name))
        .click(Selector('a').withText(testdata.act2.details__name))
        .expect(Selector('.payment-create-btn').exists).notOk()
        
        // Check that this user cannot edit payments
        .click(Selector('button').withText('Betaling').nth(0))
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

test('Check that normal user can register payment under certain circumstances', async t => {

    await login(t, 'familieraadgiver', 'sagsbehandler') 

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))
        .click(Selector('a').withText(testdata.act1.details__name))
        .expect(Selector('td input.field-amount').exists).ok()
        .expect(Selector('td input[type="date"]').exists).ok()

        .click(Selector('a').withText(testdata.appr1.name))
        .click(Selector('a').withText(testdata.act2.details__name))
        .expect(Selector('td input.field-amount').exists).notOk()
        .expect(Selector('td input[type="date"]').exists).notOk()

        .click(Selector('a').withText(testdata.appr1.name))
        .click(Selector('a').withText(testdata.act3.details__name))
        .expect(Selector('td input.field-amount').exists).notOk()
        .expect(Selector('td input[type="date"]').exists).notOk()

        .click(Selector('a').withText(testdata.appr1.name))
        .click(Selector('a').withText(testdata.act4.details__name))
        .expect(Selector('td input.field-amount').exists).ok()
        .expect(Selector('td input[type="date"]').exists).ok()
        .typeText(Selector('td input.field-amount').nth(0), '200', {replace: true})
        .typeText(Selector('td input[type="date"]').nth(0), createDate(6), {replace: true})
        .click(Selector('button').withText('Gem'))
        .expect(Selector('span.amount-paid').exists).ok()
        .expect(Selector('span.date-paid').exists).ok()
})

test('Check that improved user can register payment at all times', async t => {

    await login(t, 'regelmotor', 'regelmotor')

    await useSelectBox(t, '#field-case-worker', 'familieraadgiver)')

    await t
        .click(Selector('a').withText(testdata.case1.name))
        .click(Selector('a').withText(testdata.appr1.name))
        .click(Selector('a').withText(testdata.act1.details__name))
        .expect(Selector('td input.field-amount').exists).ok()
        .expect(Selector('td input[type="date"]').exists).ok()

        .click(Selector('a').withText(testdata.appr1.name))
        .click(Selector('a').withText(testdata.act2.details__name))
        .expect(Selector('td input.field-amount').exists).ok()
        .expect(Selector('td input[type="date"]').exists).ok()

        .click(Selector('a').withText(testdata.appr1.name))
        .click(Selector('a').withText(testdata.act3.details__name))
        .expect(Selector('td input.field-amount').exists).ok()
        .expect(Selector('td input[type="date"]').exists).ok()

        .click(Selector('a').withText(testdata.appr1.name))
        .click(Selector('a').withText(testdata.act4.details__name))
        .expect(Selector('td input.field-amount').exists).ok()
        .expect(Selector('td input[type="date"]').exists).ok()
        .typeText(Selector('td input.field-amount').nth(0), '200', {replace: true})
        .typeText(Selector('td input[type="date"]').nth(0), createDate(6), {replace: true})
        .click(Selector('button').withText('Gem'))
        .expect(Selector('span.amount-paid').exists).notOk()
        .expect(Selector('span.date-paid').exists).notOk()

        // Check that we get a warning if trying to set paid date in the near future
        .click(Selector('a').withText(testdata.appr1.name))
        .click(Selector('a').withText(testdata.act2.details__name))
        .typeText(Selector('td input[type="date"]').nth(0), createDate(1), {replace: true})
        .expect(Selector('.popover').exists).ok()
        .click(Selector('a').withText(testdata.appr1.name))
        .click(Selector('a').withText(testdata.act3.details__name))
        .typeText(Selector('td input[type="date"]').nth(0), createDate(1), {replace: true})
        .expect(Selector('.popover').exists).ok()
})