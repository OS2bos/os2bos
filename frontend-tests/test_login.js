// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { user } from '../utils/roles.js'

fixture `User login tests`// declare the fixture
    .page `localhost:8000`;  // specify the start page

test('User login/logout', async t => {
    
    await t
        .useRole( user )
        .expect(Selector('.notification.success').exists).ok()
        //.setNativeDialogHandler(() => true)
        //.click(Selector('button').withText('Log ud'))
        //.expect(Selector('.msg').nth(1).innerText).contains('Du er nu logget ud')
})
