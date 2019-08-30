<template>
    
    <tr v-if="visible"
        class="act-list-item" 
        :class="{ [act.group]: act.group, 'meta-row': act.is_meta, 'sub-row': act.group }" 
        :title="act.note" 
        @click="act.is_meta ? toggleGroup(act.id) : false">
        <td style="width: 4.5rem;">
            <template v-if="!act.is_meta">
                <input type="checkbox" :id="`check-${ act.id }`" disabled>
                <label class="disabled" :for="`check-${ act.id }`"></label>
            </template>
            <div v-else class="dropdown-arrow" :class="{'toggled': toggled}">▼</div>
        </td>
        <td style="width: 5.5rem;">
            <div class="mini-label" v-html="statusLabel(act.status)"></div>
        </td>
        <td>
            <router-link v-if="!act.is_meta" :to="`/activity/${ act.id }`">{{ activityId2name(act.details) }}</router-link>
            <span v-else>{{ activityId2name(act.details) }}</span>
        </td>
        <td>
            {{ act.payment_plan.recipient_name }}
            <span v-if="act.payment_plan.recipient_type === 'COMPANY'">
                CVR
            </span>
            {{ act.payment_plan.recipient_id }}
        </td>
        <td class="nowrap">{{ displayDate(act.start_date) }}</td>
        <td class="nowrap">{{ displayDate(act.end_date) }}</td>
        <td class="nowrap right">
            <span v-if="act.status === 'GRANTED'">{{ displayDigits(act.total_cost_this_year) }} kr</span>
            <span v-if="act.status === 'DRAFT'" class="dim">{{ displayDigits(act.total_cost_this_year) }} kr</span>
        </td>
        <td class="nowrap right">
            <span v-if="act.status === 'EXPECTED'" class="expected">{{ displayDigits(act.total_cost_this_year) }} kr</span>
        </td>
    </tr>

</template>

<script>

    import { json2jsDate } from '../filters/Date.js'
    import { cost2da } from '../filters/Numbers.js'
    import { activityId2name, displayStatus } from '../filters/Labels.js'

    export default {
    
        props: [
            'act'
        ],
        data: function() {
            return {
                visible: true,
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
                this.$emit('toggle', group_id)
            }
        },
        created: function() {
            if (this.act.group) {
                this.visible = false
            }
        }
    }

</script>

<style>

    .act-list-item.meta-row {
        cursor: pointer;
    }

    .act-list-item.sub-row td {
        background-color: hsl(var(--color1), 66%, 92%);
    }

    .act-list-item .dropdown-arrow {
        line-height: 1;
        height: 1.5rem;
        width: 1.5rem;
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: hidden;
        text-align: center;
        transition: transform .25s;
    }

    .act-list-item .dropdown-arrow.toggled {
        transform: rotate(-180deg);
    }

</style>