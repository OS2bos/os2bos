import vrt from '../utils/vrt.js'
import { login } from '../utils/logins.js'


fixture `Check for visual regression`
.page('http://localhost:8080/#/')

test('Homepage', async t => {

    await login(t)
    await vrt('check_for_visual_regression', 'homepage', 'url: http://localhost:8080/#/')

})