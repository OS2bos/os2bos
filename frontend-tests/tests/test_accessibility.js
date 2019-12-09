import { login } from '../utils/logins.js'
import { axe, options } from '../utils/axe.js'
import { Selector } from 'testcafe'
import logs from '../utils/logs.js'
import baseurl from '../utils/url.js'

fixture `Test accessibility with AXE`
    .page(baseurl)
    .beforeEach(async t => { await login(t) })
    .afterEach(async t => {
        await axe(t, null, options)
        logs()
    })

test
('Home page', async t => {
    await t.expect(Selector('h1').innerText).contains('Mine sager')
})

test
('Case page', async t => {
    await t
        .click(Selector('a').withAttribute('href', '#/case/1/'))
        .expect(Selector('h1').innerText).contains('Hovedsag')
})

test
.skip
('Appropriation page', async t => {
    await t
    .click(Selector('a').withAttribute('href', '#/case/1/'))
    .click(Selector('a').withAttribute('href', '#/appropriation/1/'))
    .expect(Selector('h1').innerText).contains('Bevillingsskrivelse')
})

test
.skip
('Activity page', async t => {
    await t.navigateTo('/#/activity/1/')
    await t.expect(Selector('h1').innerText).contains('Udgift')
})