import { axeCheck, createReport } from 'axe-testcafe'

const axeContext = { 
    exclude: [['.msg']]
}

const axeOptions = {
    runOnly: {
        type: 'tag',
        values: ['wcag2a', 'wcag2aa']
    }
}

async function axe(t) {
    const { error, violations } = await axeCheck(t, axeContext, axeOptions);
    await t.expect(violations.length === 0).ok(createReport(violations))
}

export { 
    axe
}