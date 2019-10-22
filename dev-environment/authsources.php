<?php

$config = array(

    'admin' => array(
        'core:AdminPassword',
    ),

    'example-userpass' => array(
        'exampleauth:UserPass',
        'admin:admin' => array(
            'uid' => array('1'),
            'email' => 'user2@example.com',
            'username' => 'admin',
            'first_name' => 'IT',
            'last_name' => 'Guy',
            'bos_profile' => 'admin'
        ),
        'familieleder:sagsbehandler' => array(
            'uid' => array('2'),
            'email' => 'user2@example.com',
            'username' => 'familieleder',
            'first_name' => 'Familie',
            'last_name' => 'Leder',
            'bos_profile' => 'grant'
        ),
        'familieraadgiver:sagsbehandler' => array(
            'uid' => array('3'),
            'email' => 'user2@example.com',
            'username' => 'familieraadgiver',
            'first_name' => 'Familie',
            'last_name' => 'Raadgiver',
            'bos_profile' => 'edit'
        ),
        'ungeleder:sagsbehandler' => array(
            'uid' => array('4'),
            'email' => 'user2@example.com',
            'username' => 'ungeleder',
            'first_name' => 'Unge',
            'last_name' => 'Leder',
            'bos_profile' => 'readonly'
        ),
        'ungeraadgiver:sagsbehandler' => array(
            'uid' => array('5'),
            'email' => 'user2@example.com',
            'username' => 'ungeraadgiver',
            'first_name' => 'Unge',
            'last_name' => 'Raadgiver',
            'bos_profile' => ''
        ),
    ),

);

