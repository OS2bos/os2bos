import { login } from '../utils/logins.js'
import { Selector } from 'testcafe'


fixture `Test SSO login`
    .page `http://localhost:8080/`

test('Login', async t => {

    await login(t)
    await t.expect(Selector('.useractions').exists).ok()

})