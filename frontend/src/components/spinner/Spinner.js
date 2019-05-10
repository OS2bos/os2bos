import './spinner.css'

const spinner = function() {

    const spin_el = document.createElement('div')
    spin_el.id = 'spinner'
    spin_el.role = 'alert'

    const
        testSpin = function() {
            if (document.getElementById('spinner')) {
                return true
            } else {
                return false
            }
        },
        spinOn = function() {
            if (!testSpin()) {
                document.body.appendChild(spin_el)
            }
        },
        spinOff = function() {
            if (testSpin()) {
                document.body.removeChild(spin_el)
            }
        }

    return {
        spinOn,
        spinOff
    }
}

export default spinner()