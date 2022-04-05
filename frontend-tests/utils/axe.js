import { checkForViolations } from '@testcafe-community/axe'

async function axe(t) {
    const axeContext = { exclude: [['.msg']] }
    const axeOptions = { runOnly: { type: 'tag', values: ['wcag2a', 'wcag2aa'] }, rules: {} }

    await checkForViolations(t, axeContext, axeOptions);
}

export { 
    axe
}