function leadZero(num) {
    if (parseInt(num) < 10) {
        return `0${ num}`
    } else {
        return num
    }
}

export {
    leadZero
}