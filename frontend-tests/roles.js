import { Role, Selector } from 'testcafe'

const user = Role('http://localhost:8000/#/login', async t => {

    await t
        .typeText('#username', 'ungeraadgiver')
        .typeText('#password', 'sagsbehandler')
        .click(Selector('input').withAttribute('type','submit'))
        
}, { preserveUrl: true })

export {
    user
}