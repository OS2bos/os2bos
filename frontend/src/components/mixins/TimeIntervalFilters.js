/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

 export default {

  data: function() {
    return {
        intervals: [
            {
                id: 'current-week',
                name: 'Denne uge',
            },
            {
                id: 'previous-week',
                name: 'Sidste uge',
            },
            {
                id: 'next-week',
                name: 'Næste uge',
            },
            {
                id: 'current-month',
                name: 'Denne måned',
            },
            {
                id: 'previous-month',
                name: 'Sidste måned',
            },
            {
                id: 'next-month',
                name: 'Næste måned',
            },
            {
                id: 'current-year',
                name: 'Dette år',
            },
            {
                id: 'previous-year',
                name: 'Sidste år',
            },
            {
                id: 'next-year',
                name: 'Næste år',
            },
            {
                id: 'date-range',
                name: 'Til og fra dato',
            }
        ]

    }
  },
  methods: {
    changeTimeInterval: function(interval) {
        this.range_dates = false

        // Current week //
        if (interval === 'current-week') {
            this.$store.commit('setPaymentSearchFilter', {
                'date__gte': '',
                'date__lte': '',
                'date_week': 'current',
                'date_month': '',
                'date_year': ''
            })
        }
        // Previous week //
        else if (interval === 'previous-week') {
            this.$store.commit('setPaymentSearchFilter', {
                'date__gte': '',
                'date__lte': '',
                'date_week': 'previous',
                'date_month': '',
                'date_year': ''
            })
        }
        // Next week //
        else if (interval === 'next-week') {
            this.$store.commit('setPaymentSearchFilter', {
                'date__gte': '',
                'date__lte': '',
                'date_week': 'next',
                'date_month': '',
                'date_year': ''
            })
        }
        // Current month //
        else if (interval === 'current-month') {
            this.$store.commit('setPaymentSearchFilter', {
                'date__gte': '',
                'date__lte': '',
                'date_week': '',
                'date_month': 'current',
                'date_year': ''
            })
        }
        // Previous month //
        else if (interval === 'previous-month') {
            this.$store.commit('setPaymentSearchFilter', {
                'date__gte': '',
                'date__lte': '',
                'date_week': '',
                'date_month': 'previous',
                'date_year': ''
            })
        }
        // Next month //
        else if (interval === 'next-month') {
            this.$store.commit('setPaymentSearchFilter', {
                'date__gte': '',
                'date__lte': '',
                'date_week': '',
                'date_month': 'next',
                'date_year': ''
            })
        }
        // Current year //
        else if (interval === 'current-year') {
            this.$store.commit('setPaymentSearchFilter', {
                'date__gte': '',
                'date__lte': '',
                'date_week': '',
                'date_month': '',
                'date_year': 'current',
            })
        }
        // Previous year //
        else if (interval === 'previous-year') {
            this.$store.commit('setPaymentSearchFilter', {
                'date__gte': '',
                'date__lte': '',
                'date_week': '',
                'date_month': '',
                'date_year': 'previous'
            })
        }
        // Next year //
        else if (interval === 'next-year') {
            this.$store.commit('setPaymentSearchFilter', {
                'date__gte': '',
                'date__lte': '',
                'date_week': '',
                'date_month': '',
                'date_year': 'next'
            })
        }
        // Range of dates //
        else if (interval === 'date-range') {
            this.$store.commit('setPaymentSearchFilter', {
                'date__gte': '',
                'date__lte': '',
                'date_week': '',
                'date_month': '',
                'date_year': ''
            })
            this.range_dates = true
        }
        else {
            this.$store.commit('setPaymentSearchFilter', {
                'date__gte': '',
                'date__lte': '',
                'date_week': '',
                'date_month': '',
                'date_year': ''
            })
        }
        if (this.interval !== interval && this.interval || interval) {
            this.$store.commit('setPaymentSearchFilter', {'interval': interval})
            this.$store.dispatch('fetchSearchPayments')
        } else if (!this.interval) {
            this.$store.commit('setPaymentSearchFilter', {'interval': 'date-range'})
            this.range_dates = true
        }
    }
  }
}