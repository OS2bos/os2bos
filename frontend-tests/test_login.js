// Testing with Testcafe : https://devexpress.github.io/testcafe/documentation/getting-started/

import { Selector } from 'testcafe'
import { user } from './roles.js'

fixture `User login tests`// declare the fixture
    .page `http://localhost:8080/#/my-cases`  // specify the start page

test('User login/logout', async t => {
    
    await t
        .useRole( user )
        .navigateTo('http://localhost:8080/#/my-cases')
        .expect(Selector('.useractions p strong').innerText).contains('ungeraadgiver')
        //.click(Selector('button').withText('Log ud'))
        //.expect(Selector('.msg').nth(1).innerText).contains('Du er logget ud')
})
