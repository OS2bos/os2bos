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
                id: 1,
                name: 'Denne uge',
            },
            {
                id: 2,
                name: 'Sidste uge',
            },
            {
                id: 3,
                name: 'Næste uge',
            },
            {
                id: 4,
                name: 'Denne måned',
            },
            {
                id: 5,
                name: 'Sidste måned',
            },
            {
                id: 6,
                name: 'Næste måned',
            },
            {
                id: 7,
                name: 'Dette år',
            },
            {
                id: 8,
                name: 'Til og fra dato',
            }
        ]
    }
  },
  methods: {
    changeTimeInterval: function(interval) {
        this.range_dates = false

        // Current week //
        if (interval === 1) {
            this.$route.query.paid_date_or_date__gte = getWeekDay(0)
            this.$route.query.paid_date_or_date__lte = getWeekDay(-6)
        }
        // Previous week //
        else if (interval === 2) {
            this.$route.query.paid_date_or_date__gte = getWeekDay(7)
            this.$route.query.paid_date_or_date__lte = getWeekDay(1)
        }
        // Next week //
        else if (interval === 3) {
            this.$route.query.paid_date_or_date__gte = getWeekDay(-7)
            this.$route.query.paid_date_or_date__lte = getWeekDay(-13)
        }
        // Current month //
        else if (interval === 4) {
            this.$route.query.paid_date_or_date__gte = firstDayMonth()
            this.$route.query.paid_date_or_date__lte = lastDayMonth()
        }
        // Previous month //
        else if (interval === 5) {
            this.$route.query.paid_date_or_date__gte = firstOfPreviousMonth()
            this.$route.query.paid_date_or_date__lte = lastOfPreviousMonth()
        }
        // Next month //
        else if (interval === 6) {
            this.$route.query.paid_date_or_date__gte = firstOfNextMonth()
            this.$route.query.paid_date_or_date__lte = lastOfNextMonth()
        }
        // Current year //
        else if (interval === 7) {
            this.$route.query.paid_date_or_date__gte = firstOfCurrentYear()
            this.$route.query.paid_date_or_date__lte = lastOfCurrentYear()
        }
        // Range of dates //
        else if (interval === 8) {
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