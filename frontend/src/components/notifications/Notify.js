/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import './notify.css'

function notify(message, type, response) {
    /* Method 'notify': Displays a notification on the page for 10 seconds
     * argument 'message': The message to be displayed, ex. 'Something was updated'
     * optional argument 'type': The type of message to be displayed. Available options: 'success', 'error'
     * optional argument 'response': Responsetext/Responsebody from JSON error response. Comes in the form of { [key]: [message_value] }
     */

    let notify_container
    let notify_el = document.createElement('div')

    // Check if notification container already exists
    // and if not, create it
    if (!document.querySelector('.notification-container')) {
        notify_container = document.createElement('div')
        notify_container.className = 'notification-container'
        document.getElementById('app-main').appendChild(notify_container)
    } else {
        notify_container = document.querySelector('.notification-container')
    }

    // Create notification
    let msg = `${message}`
    if (response) {
        const keys = Object.keys(response)
        for (let k in keys) {   
            msg = msg + ': ' + response[keys[k]]
        }
    }
    if (type === 'error') {
        notify_el.className = 'notification notification-error'
    } else if (type === 'success') {
        notify_el.className = 'notification success'
    } else {
        notify_el.className = 'notification'
    }
    notify_el.role = 'status'
    notify_el.innerHTML = `<div class="msg">${ msg }</div><button class="remove-alert" title="Luk"></button>`

    // Display notification
    notify_container.appendChild(notify_el)
    setTimeout(function () {
        notify_el.classList.add('show')
        setTimeout(function () {
            notify_el.classList.remove('show')
            setTimeout(function () {
                if (notify_el) { // Notification might have been removed by user
                    notify_container.removeChild(notify_el)
                }
            }, 500)
        }, 10000)
    }, 100)

    // Enable user to remove notification from view
    notify_el
        .querySelector('.remove-alert')
        .addEventListener('click', function(event) {
            notify_el.classList.remove('show')  
        })
}

export default notify