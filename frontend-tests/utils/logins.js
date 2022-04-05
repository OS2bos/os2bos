import { Selector } from 'testcafe'
import { Role } from 'testcafe'
import baseurl from '../utils/url.js'

let username = 'familieleder',
    password = 'sagsbehandler'

async function login(t, user, pass) { // Can be called with optional parameters for username and password
    if (user) {
        username = user
    }
    if (pass) {
        password = pass
    }

    if (Selector('.logintext').exists) {
        await t
            .typeText('#username', username)
            .typeText('#password', password)
            .click(Selector('button').withExactText('Login'))
    }
        
}

const familieleder = Role(baseurl, async t => {
    await t
        .typeText('#username', 'familieleder')
        .typeText('#password', 'sagsbehandler')
        .click(Selector('button').withExactText('Login'))
})

const familieraadgiver = Role(baseurl, async t => {
    await t
        .typeText('#username', 'familieraadgiver')
        .typeText('#password', 'sagsbehandler')
        .click(Selector('button').withExactText('Login'))
})

const admin = Role(baseurl, async t => {
    await t
        .typeText('#username', 'admin')
        .typeText('#password', 'admin')
        .click(Selector('button').withExactText('Login'))
})

const regelmotor = Role(baseurl, async t => {
    await t
        .typeText('#username', 'regelmotor')
        .typeText('#password', 'regelmotor')
        .click(Selector('button').withExactText('Login'))
})

export {
    login,
    familieleder,
    familieraadgiver,
    admin,
    regelmotor
}