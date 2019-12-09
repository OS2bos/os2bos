import { login } from '../utils/logins.js'
import { Selector } from 'testcafe'
import baseurl from '../utils/url.js'


fixture `Test SSO login`
    .page(baseurl)

test('Login', async t => {

    await login(t)
    await t.expect(Selector('.useractions').exists).ok()

})