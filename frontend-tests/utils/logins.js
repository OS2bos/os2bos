async function loginAsUngeraadgiver(t) {
    await t
        .navigateTo('http://localhost:8080/#/login')
        .typeText('#username', 'ungeraadgiver')
        .typeText('#password', 'sagsbehandler')
        .click('input[type="submit"]')
}

export { loginAsUngeraadgiver }