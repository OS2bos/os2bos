import { Selector } from 'testcafe'

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

async function useSelectBox(t, select_id, select_option) {
    await t.click(select_id)
    if (select_option) {
        const option_exists = await Selector(`${ select_id } option`).withText(select_option).exists
        if (option_exists) {
            await t.click(Selector(`${ select_id } option`).withText(select_option))
        } else {
            await t.click(Selector(`${ select_id } option`).nth(1))
        }
    } else {
        await t.click(Selector(`${ select_id } option`).nth(1))
    }
}

export {
    leadZero,
    randNum,
    createDate,
    useSelectBox
}