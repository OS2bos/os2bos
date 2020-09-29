<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <div>
        <h3 class="act-list-heading">
            {{ title }}
        </h3>

        <div class="act-list-row act-list-header">
            <div></div>
            <div>Status</div>
            <div>Ydelse</div>
            <div>Supplerende oplysninger</div>
            <div>Udbetales til</div>
            <div>Start</div>
            <div>Slut</div>
            <div>Senest ændret</div>
            <div class="right">
                <span v-if="selectedValue === '1'">Udgift i år</span>
                <span v-if="selectedValue === '2'">Udgift pr. år</span>
                <span v-if="selectedValue === '3'">Samlet udgift</span>
            </div>
            <div class="right">
                <span v-if="selectedValue === '1'">Forventet udgift i år</span>
                <span v-if="selectedValue === '2'">Forventet udgift pr. år</span>
                <span v-if="selectedValue === '3'">Forventet samlet udgift</span>
            </div>
        </div>

        <button 
            class="act-list-collapse-button" 
            @click="toggleOld" 
            v-if="old_acts && old_acts.length > 0">
            <span v-if="!display_old">
                <span class="material-icons">expand_more</span>
                Vis {{ old_acts.length }} udgåede {{ title }}
                <span class="material-icons">expand_more</span>
            </span>
            <span v-else>
                <span class="material-icons">expand_less</span>
                Skjul {{ old_acts.length }} udgåede {{ title }}
                <span class="material-icons">expand_less</span>
            </span>
        </button>
        
        <activity-list-group 
            v-for="acts in act_groups" 
            :activities="acts" 
            :key="acts.id" 
            :display-old="display_old" />
    </div>
</template>

<script>
import ActivityListGroup from './ActListGroup.vue'
import PermissionLogic from '../../mixins/PermissionLogic.js'

export default {
    mixins: [
        PermissionLogic
    ],
    components: {
        ActivityListGroup
    },
    props: [
        'title',
        'activities'
    ],
    data: function() {
        return {
            display_old: false
        }
    },
    computed: {
        act_groups: function() {
            if (this.activities) {
                let old_acts = this.activities,
                    groups = []
                for (let act of old_acts) {
                    if (act.modifies === null) {
                        let group = [act]
                        this.addModifierAct(group, act.id, old_acts)
                        groups.push(group)
                    }
                }
                return groups
            }
        },
        old_acts: function() {
            if (this.activities) {
                return this.activities.filter(function(act) {
                    return act.is_old
                })
            }
        },
        approvable_acts: function() {
            return this.$store.getters.getCheckedItems
        },
        selectedValue: function(){
            return this.$store.getters.getSelectedCostCalc
        }
    },
    methods: {
        addModifierAct(group, id, act_list) {
            let modifiers = act_list.filter(function(a) {
                return a.modifies === id
            })
            if (modifiers.length > 0) {
                for (let m in modifiers) {
                    group.push(modifiers[m])
                    this.addModifierAct(group, modifiers[m].id, act_list)
                }
            } else {
                return group
            }
        },
        toggleOld: function() {
            this.display_old = !this.display_old
        }
    }
}
</script>

<style>

    .act-list-heading {
        padding: 1.5rem 0 .5rem;
    }

    .act-list-row.act-list-header {
        background-color: var(--grey0);
    }

    .act-list-row.act-list-header > div {
        color: var(--grey10);
        opacity: .66;
        vertical-align: middle;
        font-weight: normal;
        font-size: .85rem;
        padding-bottom: .25rem;
    }

    .act-list-collapse-button {
        padding: 0;
        display: block;
        margin: 0 auto .25rem;
        width: 100%;
        border: solid 1px var(--grey1);
        box-shadow: none;
    }
    
</style>