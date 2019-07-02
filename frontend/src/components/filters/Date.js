function json2js(jsondatetime) {
    if (jsondatetime) {
        const dt = new Date(jsondatetime)
        return `${ dt.getDate() }. ${ strMonth(dt.getMonth()) } ${ dt.getFullYear() }, ${ leadZero(dt.getHours()) }:${ leadZero(dt.getMinutes()) }`
    } else {
        return '-'
    }
}

function leadZero(number) {
    if (number < 10) {
        return `0${ number }`
    } else {
        return number
    }
}

function strMonth(month_index) {
    const months = [
        'jan', 'feb', 'mar', 'apr', 'maj', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec'
    ]
    return months[month_index]
}

export {
    json2js
}