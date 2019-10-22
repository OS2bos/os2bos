<?php
/*
 * Overwrites the configuration of SimpleSAMLphp from
 * kristophjunge/docker-test-saml-idp.
 *
 */

include('base_config.php');

$config['baseurlpath'] = getenv('SIMPLESAMLPHP_BASEURLPATH');

?>
