<?php

$config = array(

    'admin' => array(
        'core:AdminPassword',
    ),

    'example-userpass' => array(
        'exampleauth:UserPass',
        'admin:admin' => array(
            'email' => 'user2@example.com',
            'username' => 'admin',
            'first_name' => 'IT',
            'last_name' => 'Guy',
            'team' => 'S-DIG',
            'bos_profile' => 'admin'
        ),
        'familieleder:sagsbehandler' => array(
            'email' => 'user2@example.com',
            'username' => 'familieleder',
            'first_name' => 'Familie',
            'last_name' => 'Leder',
            'team' => 'Familierådgivning',
            'bos_profile' => 'grant'
        ),
        'familieraadgiver:sagsbehandler' => array(
            'email' => 'user2@example.com',
            'username' => 'familieraadgiver',
            'first_name' => 'Familie',
            'last_name' => 'Raadgiver',
            'bos_profile' => 'edit'
        ),
        'ungeleder:sagsbehandler' => array(
            'email' => 'user2@example.com',
            'username' => 'ungeleder',
            'first_name' => 'Unge',
            'last_name' => 'Leder',
            'bos_profile' => 'readonly'
        ),
        'ungeraadgiver:sagsbehandler' => array(
            'email' => 'user2@example.com',
            'username' => 'ungeraadgiver',
            'first_name' => 'Unge',
            'last_name' => 'Raadgiver',
            'bos_profile' => ''
        ),
        'heidi:heidi' => array(
            'email' => 'hbb@balk.dk',
            'username' => 'heidi',
            'first_name' => 'Heidi',
            'last_name' => 'Engelhardt Bebe',
            'bos_profile' => 'admin'
        ),
        'regelmotor:regelmotor' => array(
            'email' => 'user2@example.com',
            'username' => 'regelmotor',
            'first_name' => 'regelmotor',
            'last_name' => 'regelmotor',
            'bos_profile' => 'workflow_engine'
        ),
    ),

);

