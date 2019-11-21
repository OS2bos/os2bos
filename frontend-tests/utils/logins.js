import { Selector } from 'testcafe'

let username = 'familieleder',
    password = 'sagsbehandler'

export async function login(t, user, pass) { // Can be called with optional parameters for username and password
    if (user) {
        username = user
    }
    if (pass) {
        password = pass
    }
    await t
        .navigateTo('http://localhost:8080/')

    if (Selector('.logintext').exists) {
        await t
            .typeText('#username', username)
            .typeText('#password', password)
            .click(Selector('button').withExactText('Login'))
    }
        
}