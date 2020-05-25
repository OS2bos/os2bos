<template>
    
    <tr v-if="visible"
        class="act-list-item" 
        :class="{ [act.group]: act.group, 'meta-row': act.is_meta, 'sub-row': act.group }" 
        :title="act.note" 
        @click="act.is_meta ? toggleGroup(act.id) : false">
        <td style="width: 3.5rem; padding: .5rem 0 0 1.25rem;">
            <template v-if="!act.is_meta && act.status !== 'GRANTED'">
                <input v-if="permissionCheck === true && this.user.profile !== 'edit'" type="checkbox" :id="`check-${ act.id }`" v-model="is_checked" @change="$emit('check', is_checked)">
                <label class="disabled" :for="`check-${ act.id }`" title="Udvælg denne ydelse"></label>
            </template>
            <div v-if="act.is_meta" class="dropdown-arrow" :class="{'toggled': toggled}">▼</div>
        </td>
        <td style="width: 6rem;">
            <div class="mini-label" v-html="statusLabel(act.status)"></div>
        </td>
        <td>
            <router-link v-if="!act.is_meta" :to="`/activity/${ act.id }`">
                {{ activityId2name(act.details) }}<br>
            </router-link>
            <span v-else>{{ activityId2name(act.details) }}</span>
            <span class="dim" v-if="act.payment_plan.fictive">(Fiktiv)</span>
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
        <td class="nowrap">{{ displayDate(act.modified) }}</td>
        <td class="nowrap right">
            {{ displayCost(act, 'granted') }}
        </td>
        <td class="nowrap right">
            <span :class="act.status === 'DRAFT' ? 'dim' : 'expected'">
                {{ displayCost(act, 'expected') }}
            </span>
        </td>
    </tr>

</template>

<script>

    import { json2jsDate } from '../filters/Date.js'
    import { cost2da } from '../filters/Numbers.js'
    import { activityId2name, displayStatus } from '../filters/Labels.js'
    import UserRights from '../mixins/UserRights.js'

    export default {

        mixins: [UserRights],
    
        props: [
            'act',
            'checked',
            'selectedValue'
        ],
        data: function() {
            return {
                visible: true,
                toggled: false,
                is_checked: false,
                is_selectedValue: '1'
            }
        },
        watch: {
            checked: function() {
                this.is_checked = this.checked
            },
            selectedValue: function() {
                this.is_selectedValue = this.selectedValue
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
            },
            displayCost: function(act, column) {
                if (act.is_meta) {
                    if (column === 'granted') {
                        if (act.approved !== 0) {
                            return `${ this.displayDigits(act.approved) } kr`
                        }
                    } else {
                        if (act.expected !== act.approved) {
                            return `${ this.displayDigits(act.expected) } kr`
                        }
                    }
                } else {
                    if (column === 'granted') {
                        if (act.status === 'GRANTED' && this.selectedValue === '1') {
                            return `${ this.displayDigits(act.total_granted_this_year) } kr`
                        }
                        if (act.status === 'GRANTED' && this.selectedValue === '2') {
                            return `${ this.displayDigits(act.total_cost_full_year) } kr`
                        }
                        if (act.status === 'GRANTED' && this.selectedValue === '3') {
                            return `${ this.displayDigits(act.total_cost) } kr`
                        }
                    } else {
                        if (act.total_expected_this_year === 0 || act.total_expected_this_year !== act.total_granted_this_year && this.selectedValue === '1') {
                            return `${ this.displayDigits(act.total_expected_this_year) } kr`
                        }
                        if (act.total_expected_this_year === 0 || act.total_expected_this_year !== act.total_granted_this_year && this.selectedValue === '2') {
                            return `${ this.displayDigits(act.total_cost_full_year) } kr`
                        }
                        if (act.total_expected_this_year === 0 || act.total_expected_this_year !== act.total_granted_this_year && this.selectedValue === '3') {
                            return `${ this.displayDigits(act.total_cost) } kr`
                        }
                    }
                }
            }
        },
        created: function() {
            this.is_checked = this.checked
            this.is_selectedValue = this.selectedValue
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