import vrt from '../utils/vrt.js'
import { login } from '../utils/logins.js'
import { Selector } from 'testcafe'


fixture `Check for visual regression`
.page('http://localhost:8080/#/')

test('Homepage', async t => {

    await login(t)
    await t.expect(Selector('.useractions').exists).ok()
    //await vrt('Check for visual regression', 'Homepage')

})