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

/*
 * @param offset is the number of days in the future the day should be. Default is a random date within 6 months
 */
function createDate(offset) {
    let today = new Date(),
        local_offset = offset
    if (!offset) {
        local_offset = Math.floor(Math.random()*180)
    }
    today.setDate(today.getDate() + parseInt(local_offset))
    return `2020-${ leadZero(today.getMonth() + 1) }-${ leadZero(today.getDate()) }`
}

export {
    leadZero,
    randNum,
    createDate
}