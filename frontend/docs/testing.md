# Testing the frontend

The testing tools have been isolated from the frontend proper. This way, you don't need to enter a docker container to run tests while developing.

## E2E testing

The files and tools for E2E testing are located in `/frontend-test`

To run a test, make sure you have [NodeJS](https://nodejs.org/en/docs/) and [npm](https://docs.npmjs.com/) installed on your host machine.
Then change to the `/frontend-test` folder and run `npm run test` from a command line.

### Default browser for testing

The test will run inside a [Chrome browser](https://www.google.com/intl/en/chrome/) so we assume you have the Chrome browser installed.
If you want to run the test in another browser, open `/frontend-test/package.json` and edit the line for the _test_ script to use another browser like `firefox` or `safari`.


## Testing on external devices

You can test your local development instance in virtual machines and on other devices.
This is useful when you need to do UI tests on mobile devices or in browsers that can't be installed on your system (like old versions of Internet Explorer).
Unfortunately, this doesn't come out of the box. You'll need to set it up.

Pointing your browser to `localhost:8080` will show you the UI but this will only work on your host machine. 
In your virtual guest OS or mobile device, localhost points to something else. 
The key is to use your host's IP address rather than localhost. 
Devices *that are on your local network* are able to detect your host system IP and display the UI.
Virtual machines will generally also be able to pinpoint your development instance by IP.

### Set it up

First, find your host system IP address on your local network. 
There are various ways to do this depending on your system. 
Your IP could be something like `10.0.0.23`

Open `/docker-compose.yml` and find the following bit of text
```
  environment:
    - SIMPLESAMLPHP_BASEURLPATH=http://localhost:8080/simplesaml/
    - SIMPLESAMLPHP_SP_ENTITY_ID=http://localhost:8080
    - SIMPLESAMLPHP_SP_ASSERTION_CONSUMER_SERVICE=http://localhost:8080/api/saml2_auth/acs/
```

Replace all mentions of *localhost* with your IP like this
```
  environment:
    - SIMPLESAMLPHP_BASEURLPATH=http://10.0.0.23:8080/simplesaml/
    - SIMPLESAMLPHP_SP_ENTITY_ID=http://10.0.0.23:8080
    - SIMPLESAMLPHP_SP_ASSERTION_CONSUMER_SERVICE=http://10.0.0.23:8080/api/saml2_auth/acs/
```

Open `/dev-environment/dev-settings.ini` and find the following bit of text
```
  ALLOWED_HOSTS=localhost,bev
```

Add your IP to the line like this
```
  ALLOWED_HOSTS=localhost,bev,10.0.0.23
```

In the command line, kill and reboot your development instance to use the new configuration.
First with CTRL+C and then
```
  docker-compose down -v
  docker-compose up
```
You should now be able to point a browser in your VM or mobile device to `10.0.0.23:8080` and see the frontend working.
