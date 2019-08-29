<template>
    
    <tr :class="{ 'expected-row': data.status === 'EXPECTED', 'adjustment-row': data.modifies }" :title="data.note">
        <td style="width: 4.5rem;">
            <input type="checkbox" :id="`check-${ data.id }`" disabled>
            <label class="disabled" :for="`check-${ data.id }`"></label>
        </td>
        <td style="width: 5.5rem;">
            <div class="mini-label" v-html="statusLabel(data.status)"></div>
        </td>
        <td>
            <router-link :to="`/activity/${ data.id }`">{{ activityId2name(data.details) }}</router-link>
            <span v-if="data.activity_type === 'MAIN_ACTIVITY'" class="act-label"><br>Hovedydelse</span>
        </td>
        <td>
            {{ data.payment_plan.recipient_name }}
            <span v-if="data.payment_plan.recipient_type === 'COMPANY'">
                CVR
            </span>
            {{ data.payment_plan.recipient_id }}
        </td>
        <td class="nowrap">{{ displayDate(data.start_date) }}</td>
        <td class="nowrap">{{ displayDate(data.end_date) }}</td>
        <td class="nowrap right">
            <span v-if="data.status === 'GRANTED'">{{ displayDigits(data.total_cost_this_year) }} kr</span>
            <span v-if="data.status === 'DRAFT'" class="dim">{{ displayDigits(data.total_cost_this_year) }} kr</span>
        </td>
        <td class="nowrap right">
            <span v-if="data.status === 'EXPECTED'" class="expected">{{ displayDigits(data.total_cost_this_year) }} kr</span>
        </td>
    </tr>

</template>

<script>

    import { json2jsDate } from '../filters/Date.js'
    import { cost2da } from '../filters/Numbers.js'
    import { activityId2name, displayStatus } from '../filters/Labels.js'

    export default {
    
        props: [
            'data'
        ],
        methods: {
            statusLabel: function(status) {
                return displayStatus(status)
            },
            displayDate: function(dt) {
                return json2jsDate(dt)
            },
            displayDigits: function(num) {
                return cost2da(num)
            },
            activityId2name: function(id) {
                return activityId2name(id)
            }
        }
        
    }

</script>