import vrt from '../utils/vrt.js'
import { login } from '../utils/logins.js'
import baseurl from '../utils/url.js'


fixture `Check for visual regression`
.page(baseurl)

test.skip('Homepage', async t => {

    await login(t)
    await vrt('check_for_visual_regression', 'homepage', 'url: http://localhost:8080/')

})