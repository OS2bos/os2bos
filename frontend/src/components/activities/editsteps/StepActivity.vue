<!-- Copyright (C) 2020 Magenta ApS, http://magenta.dk.
   - Contact: info@magenta.dk.
   -
   - This Source Code Form is subject to the terms of the Mozilla Public
   - License, v. 2.0. If a copy of the MPL was not distributed with this
   - file, You can obtain one at https://mozilla.org/MPL/2.0/. -->

<template>
    <div class="act-create-step">
        <h2>Ydelse</h2>
        <status :editable="true" />
        <fictional :editable="true" />
        <activity :editable="true" />
        <note :editable="true" />
    </div>
</template>

<script>
import Status from '../edittypes/Status.vue'
import Activity from '../edittypes/Activity.vue'
import Note from '../edittypes/Note.vue'
import Fictional from '../../payments/edittypes/Fictional.vue'

export default {

    components: {
        Status,
        Activity,
        Note,
        Fictional
    }

}
</script>