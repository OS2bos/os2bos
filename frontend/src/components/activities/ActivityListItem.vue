<template>
    
    <tr class="act-list-item" 
        :class="{ [data.group]: data.group, 'meta-row': data.is_meta, 'sub-row': data.group }" 
        :title="data.note" 
        @click="data.is_meta ? toggleGroup(data.id) : false">
        <td style="width: 4.5rem;">
            <template v-if="!data.is_meta">
                <input type="checkbox" :id="`check-${ data.id }`" disabled>
                <label class="disabled" :for="`check-${ data.id }`"></label>
            </template>
            <div v-else class="dropdown-arrow">▼</div>
        </td>
        <td style="width: 5.5rem;">
            <div class="mini-label" v-html="statusLabel(data.status)"></div>
        </td>
        <td>
            <router-link v-if="!data.is_meta" :to="`/activity/${ data.id }`">{{ activityId2name(data.details) }}</router-link>
            <span v-else>{{ activityId2name(data.details) }}</span>
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
        data: function() {
            return {
                toggled: false
            }
        },
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
            },
            toggleGroup: function(group_id) {
                // identify who is in group
            }
        }
        
    }

</script>

<style>

    .act-list-item.meta-row {
        cursor: pointer;
    }

    .act-list-item.sub-row {
        
    }

    .act-list-item.sub-row td {
        background-color: hsl(var(--color1), 66%, 92%);
    }

    .act-list-item .dropdown-arrow {
        line-height: 1;
        height: 1rem;
        width: 1rem;
        text-align: center;
        transition: transform .5s;
    }

    .act-list-item .dropdown-arrow.toggled {
        transform: rotate(-180deg);
    }

</style>