import { axeCheck, createReport } from 'axe-testcafe'

async function axe(t) {
    const { error, violations } = await axeCheck(t);
    await t.expect(violations.length === 0).ok(createReport(violations))
}

export { axe }