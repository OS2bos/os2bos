/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */

 import { 
     getWeekDay, 
     firstDayMonth, 
     lastDayMonth, 
     firstOfPreviousMonth, 
     lastOfPreviousMonth, 
     firstOfNextMonth, 
     lastOfNextMonth,
     firstOfCurrentYear,
     lastOfCurrentYear
    } from '../filters/Date.js'

 export default {

  data: function() {
    return {
        intervals: [
            {
                id: 'this-week',
                name: 'Denne uge',
            },
            {
                id: 'last-week',
                name: 'Sidste uge',
            },
            {
                id: 'next-week',
                name: 'Næste uge',
            },
            {
                id: 'this-month',
                name: 'Denne måned',
            },
            {
                id: 'last-month',
                name: 'Sidste måned',
            },
            {
                id: 'next-month',
                name: 'Næste måned',
            },
            {
                id: 'this-year',
                name: 'Dette år',
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
        if (interval === 'this-week') {
            this.$route.query.paid_date_or_date__gte = getWeekDay(0)
            this.$route.query.paid_date_or_date__lte = getWeekDay(-6)
        }
        // Previous week //
        else if (interval === 'last-week') {
            this.$route.query.paid_date_or_date__gte = getWeekDay(7)
            this.$route.query.paid_date_or_date__lte = getWeekDay(1)
        }
        // Next week //
        else if (interval === 'next-week') {
            this.$route.query.paid_date_or_date__gte = getWeekDay(-7)
            this.$route.query.paid_date_or_date__lte = getWeekDay(-13)
        }
        // Current month //
        else if (interval === 'this-month') {
            this.$route.query.paid_date_or_date__gte = firstDayMonth()
            this.$route.query.paid_date_or_date__lte = lastDayMonth()
        }
        // Previous month //
        else if (interval === 'last-month') {
            this.$route.query.paid_date_or_date__gte = firstOfPreviousMonth()
            this.$route.query.paid_date_or_date__lte = lastOfPreviousMonth()
        }
        // Next month //
        else if (interval === 'next-month') {
            this.$route.query.paid_date_or_date__gte = firstOfNextMonth()
            this.$route.query.paid_date_or_date__lte = lastOfNextMonth()
        }
        // Current year //
        else if (interval === 'this-year') {
            this.$route.query.paid_date_or_date__gte = firstOfCurrentYear()
            this.$route.query.paid_date_or_date__lte = lastOfCurrentYear()
        }
        // Range of dates //
        else if (interval === 'date-range') {
            this.$route.query.paid_date_or_date__gte = ''
            this.$route.query.paid_date_or_date__lte = ''
            this.range_dates = true
        }
        else {
            this.$route.query.paid_date_or_date__gte = ''
            this.$route.query.paid_date_or_date__lte = ''
        } 
        this.update()
    }
  }
}