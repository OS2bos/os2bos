import { login } from '../utils/logins.js'
import { axe } from '../utils/axe.js'
import logs from '../utils/logs.js'

const options = {
    runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa']
    }
}

// We are skipping a11y tests for now. This is not a public facing site
fixture `Test accessibility with AXE`
    .page `http://localhost:8080/`
    .beforeEach(async t => { await login(t) })
    .afterEach(() => logs())

test.skip('Home page', async t => {
    await axe(t, null, options)
})

test.skip('Case page', async t => {
    await t.navigateTo('http://localhost:8080/#/case/1/')
    await axe(t, null, options)
})

test.skip('Appropriation page', async t => {
    await t.navigateTo('http://localhost:8080/#/appropriation/1/')
    await axe(t, null, options)
})
