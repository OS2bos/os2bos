import { randNum, createDate } from './utils/utils.js'

// Test case data

export const case1 = {
    sbsys_id: `a${ randNum() }.${ randNum() }.${ randNum() }-regel-test`,
    effort_step: 4,
    scaling_step: 4,
    target_group: 2,
    paying_municipality: 43,
    acting_municipality: 43,
    residence_municipality: 43,
    name: "Kurt Hansen",
    cpr_number: 8888888888,
    case_worker: 4
}

export const case2 = {
    sbsys_id: `b${ randNum() }.${ randNum() }.${ randNum() }-regel-test`,
    effort_step: 2,
    scaling_step: 8,
    target_group: 1,
    district: 1,
    paying_municipality: 43,
    acting_municipality: 43,
    residence_municipality: 43,
    name: "Kurt Hansen",
    cpr_number: 8888888888,
    case_worker: 4
}

export const case3 = {
    sbsys_id: `cxx.xx.xx-${ randNum() }-${ randNum() }`,
    effort_step: 3,
    scaling_step: 6,
    target_group: 1,
    district: 2,
    paying_municipality: 43,
    acting_municipality: 43,
    residence_municipality: 43,
    name: "Lillemor Onsdag Cortazon",
    cpr_number: 5555558888,
    case_worker: 4
}

export const case4 = {
    sbsys_id: `d${ randNum() }.${ randNum() }.xx`,
    effort_step: 3,
    scaling_step: 4,
    target_group: 2,
    paying_municipality: 43,
    acting_municipality: 43,
    residence_municipality: 43,
    name: "Søren Fetterlein Sørensen",
    cpr_number: 3333336666,
    case_worker: 4
}

export const case5 = {
    sbsys_id: `exx.xx.xx-${ randNum() }-${ randNum() }`,
    effort_step: 4,
    scaling_step: 7,
    target_group: 2,
    paying_municipality: 43,
    acting_municipality: 43,
    residence_municipality: 43,
    name: "Hest von Hest",
    cpr_number: 9999998888,
    case_worker: 4
}

export const case6 = {
    sbsys_id: `fx${ randNum() }.z${ randNum() }.${ randNum() }`,
    effort_step: 3,
    scaling_step: 5,
    target_group: 2,
    paying_municipality: 43,
    acting_municipality: 43,
    residence_municipality: 43,
    name: "Pia Piasdottir",
    cpr_number: 2222221111,
    case_worker: 4
}

export const case7 = {
    sbsys_id: `g${ randNum() }.${ randNum() }.${ randNum() }-sag`,
    effort_step: 5,
    scaling_step: 7,
    target_group: 2,
    paying_municipality: 43,
    acting_municipality: 43,
    residence_municipality: 43,
    name: "Mogens Glistrup",
    cpr_number: 1000001111,
    case_worker: 3
}

export const case81 = {
    sbsys_id: `gafiltertest-${ randNum() }.${ randNum() }.${ randNum() }`,
    effort_step: 2,
    scaling_step: 4,
    target_group: 2,
    paying_municipality: 43,
    acting_municipality: 43,
    residence_municipality: 43,
    name: "John Lennon",
    cpr_number: 5555552222,
    case_worker: 2
}

export const case82 = {
    sbsys_id: `gbfiltertest-${ randNum() }.${ randNum() }.${ randNum() }`,
    effort_step: 3,
    scaling_step: 5,
    target_group: 2,
    paying_municipality: 43,
    acting_municipality: 43,
    residence_municipality: 43,
    name: "Paul Young",
    cpr_number: 2222228888,
    case_worker: 3
}

// Test appropriation data

export const appr21 = {
    sbsys_id: `h${ randNum() }.${ randNum() }.${ randNum() }-regel-test-bevilling`,
    section: 1264,
    case: null,
    id: null
}

export const appr22 = {
    sbsys_id: `i${ randNum() }.${ randNum() }.${ randNum() }-regel-test-bevilling`,
    section: 1264,
    case: null,
    id: null
}

export const appr3 = {
    sbsys_id: `jxx.xx.xx-${ randNum() }-${ randNum() }-bevil${ randNum() }`,
    section: 1264,
    case: null,
    id: null
}

export const appr4 = {
    sbsys_id: `k${ randNum() }.${ randNum() }.xx-${ randNum() }-bevil${ randNum() }`,
    section: 1264,
    case: null,
    id: null
}

export const appr5 = {
    sbsys_id: `lxx.xx.xx-${ randNum() }-${ randNum() }-bevil${ randNum() }`,
    section: 1264,
    case: null,
    id: null
}

export const appr7 = {
    sbsys_id: `m${ randNum() }.${ randNum() }.${ randNum() }-${ randNum() }-bevilling`,
    section: 1329,
    case: null,
    id: null
}

export const appr81 = {
    sbsys_id: `n${ randNum() }.${ randNum() }.${ randNum() }-${ randNum() }-bevilling`,
    section: 1315,
    case: null,
    id: null
}

export const appr82 = {
    sbsys_id: `o${ randNum() }.${ randNum() }.${ randNum() }-${ randNum() }-bevilling`,
    section: 1363,
    case: null,
    id: null
}

export const appr83 = {
    sbsys_id: `p${ randNum() }.${ randNum() }.${ randNum() }-${ randNum() }-bevilling`,
    section: 1363,
    case: null,
    id: null
}

// Test activity data
export const act22 = {
    payment_plan: {
        recipient_type: "COMPANY",
        payment_frequency: "WEEKLY",
        payment_type: "RUNNING_PAYMENT",
        payment_amount: 12,
        payment_cost_type: "FIXED",
        payment_method: "INVOICE"
    },
    status: "DRAFT",
    start_date: createDate(3),
    activity_type: "MAIN_ACTIVITY",
    details: 1752,
    appropriation: null
}

export const act71 = {
    id: null,
    payment_plan: {
        recipient_type: 'COMPANY',
        recipient_id: '25052943',
        recipient_name: "MAGENTA ApS",
        payment_type: 'INDIVIDUAL_PAYMENT',
        payment_method: "INVOICE",
        payment_cost_type: null
    },
    service_provider: {
        cvr_number: '25052943',
        name: "MAGENTA ApS",
        street: "Pilestræde",
        street_number: '43',
        zip_code: '1112',
        post_district: "København K",
        business_code: '620200',
        business_code_text: "Konsulentbistand vedrørende informationsteknologi",
        status: "NORMAL"
    },
    status: 'DRAFT',
    start_date: createDate(2),
    end_date: createDate(32),
    activity_type: "MAIN_ACTIVITY",
    details: 1733,
    appropriation: null
}

export const act72 = {
    id: null,
    payment_plan: {
        recipient_type: 'PERSON',
        recipient_id: '1111112222',
        recipient_name: 'Hannelore Hannesdottir',
        payment_frequency: "DAILY",
        payment_type: "RUNNING_PAYMENT",
        payment_amount: 120.95,
        payment_cost_type: "FIXED",
        payment_method: "SD",
    },
    status: "DRAFT",
    start_date: createDate(6),
    end_date: createDate(12),
    activity_type: "SUPPL_ACTIVITY",
    details: 1742,
    appropriation: null    
}

export const act73 = {
    id: null,
    payment_plan: {
        recipient_type: 'PERSON',
        recipient_id: '2222221111',
        recipient_name: 'Ib von Ib',
        payment_type: 'ONE_TIME_PAYMENT',
        payment_units: '5.20',
        payment_rate: 26,
        payment_date: createDate(10),
        payment_cost_type: 'GLOBAL_RATE',
        payment_method: "CASH"
    },
    status: "DRAFT",
    activity_type: "SUPPL_ACTIVITY",
    details: 1790,
    appropriation: null
}

export const act74 = {
    id: null,
    payment_plan: {
        recipient_type: 'INTERNAL',
        recipient_id: 1,
        recipient_name: 'intern modtager x',
        payment_frequency: 'BIWEEKLY',
        payment_type: 'RUNNING_PAYMENT',
        payment_units: 3,
        payment_cost_type: 'PER_UNIT',
        payment_method: "INTERNAL",
        price_per_unit: {
            amount: 100,
            start_date: createDate(1)
        }
    },
    status: "DRAFT",
    start_date: createDate(18),
    activity_type: "SUPPL_ACTIVITY",
    details: 1765,
    appropriation: null
}
