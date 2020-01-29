function leadZero(num) {
    if (parseInt(num) < 10) {
        return `0${ num}`
    } else {
        return num
    }
}

function randNum() {
    return Math.floor(Math.random() * 10 )
}

export {
    leadZero,
    randNum
}