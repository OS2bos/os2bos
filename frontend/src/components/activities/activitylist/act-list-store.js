/* Copyright (C) 2020 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

function findItem(state, item) {
    return state.checked_items.findIndex(function(ci) {
        return ci === item
    })
}
 
const state = {
    checked_items: [],
    selected_cost_calc: String(new Date().getUTCFullYear())
}
 
const getters = {
    getCheckedItems (state) {
        return state.checked_items
    },
    checkItem: (state) => (activity) => {
        if (findItem(state, activity) < 0) {
            return false
        } else {
            return true
        }
    },
    getSelectedCostCalc (state) {
        return state.selected_cost_calc
    }
}
 
const mutations = {
    setSelectedCostCalc (state, costcalc) {
        state.selected_cost_calc = costcalc
    },
    setCheckedItems (state, items) {
        state.checked_items = items
    },
    setCheckedItem (state, item) {
        if (findItem(state, item) < 0) {
            state.checked_items.push(item)
        }
    },
    removeCheckedItem (state, item) {
        const idx = findItem(state, item)
        if (idx >= 0) {
            state.checked_items.splice(idx, 1)
        }
    },
    setCheckAll (state, activities) {
        state.checked_items = activities
    },
    setUnCheckAll (state) {
        state.checked_items = []
    }
}
 
export default {
    state,
    getters,
    mutations
}