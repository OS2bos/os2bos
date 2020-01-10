======================
Frontend documentation
======================

The frontend GUI is a javascript single page application using the `VueJS framework. <https://vuejs.org/>`_
It comprises the following components:

* `VueJS <https://vuejs.org/v2/api/>`_ for templating and UI logic (view layer)
* `Vue Router <https://router.vuejs.org/api/>`_ for routing between views
* `Vuex <https://vuex.vuejs.org/api/>`_ for sharing data between Vue components
* `axios <https://github.com/axios/axios>`_ for communicating with the backend REST API
* A modified version of `Semstrap <https://iamfrank.github.io/semstrap/>`_ for basic CSS styling
* `Vue CLI <https://cli.vuejs.org/guide/>`_ for build process management
* `Testcafe <https://devexpress.github.io/testcafe/documentation/getting-started/>`_ for E2E testing


Getting started
---------------

If you have `docker <https://www.docker.com/>`_ installed and followed the `installation instructions <../README.md>`_ , you already have the frontend up and running.

Open your browser and point to ``localhost:8080`` to see the GUI in action. 
You should be able to log in with username **admin** and password **admin**.

In this configuration, the frontend lives inside a docker container running the Vue CLI server. 
When you edit files located in ``/frontend/src``, Vue CLI server uses hot reload to immediately reload the changes in your browser.

**Note:** This setup is only suitable for development use. You should make a proper production build for any public use.


Building
--------

**In development mode,** the frontend is hosted inside a docker container running Vue CLI. 
**In production mode,** you don't need this since you just need to host the bundled javascript and CSS files.

To access the docker container, run ``docker exec -it bevillingsplatform_frontend_1 bash`` from the project root on your host machine.
Now you can run various commands using `npm <https://docs.npmjs.com/>`_


Building for development
^^^^^^^^^^^^^^^^^^^^^^^^

Run ``npm run serve`` inside the frontend docker container to start Vue CLI. 
You rarely need to do this since Vue CLI starts as soon as the container is initiated.


Building for production
^^^^^^^^^^^^^^^^^^^^^^^

Run ``npm run build`` inside the frontend docker container to create a production build.
If the build is successful, you'll find the finished bundle in the ``/frontend/dist`` folder.


E2E testing
-----------

The testing tools have been isolated from the frontend proper. This way, you don't need to enter a docker container to run tests while developing.
The files and tools for E2E testing are located in ``/frontend-test``

To run a test, make sure you have `NodeJS <https://nodejs.org/en/docs/>`_ and `npm <https://docs.npmjs.com/>`_ installed on your host machine.
Then change to the ``/frontend-test`` folder and run ``npm run test`` from a command line.

Default browser for testing
^^^^^^^^^^^^^^^^^^^^^^^^^^^
The test will run inside a `Chrome browser <https://www.google.com/intl/en/chrome/>`_ so we assume you have the Chrome browser installed.
If you want to run the test in another browser, open ``/frontend-test/package.json`` and edit the line for the *test* script to use another browser like ``firefox`` or ``safari``.


Testing on external devices
---------------------------

You can test your local development instance in virtual machines and on other devices.
This is useful when you need to do UI tests on mobile devices or in browsers that can't be installed on your system (like old versions of Internet Explorer).
Unfortunately, this doesn't come out of the box. You'll need to set it up.

Pointing your browser to ``localhost:8080`` will show you the UI but this will only work on your host machine. 
In your virtual guest OS or mobile device, localhost points to something else. 
The key is to use your host's IP address rather than localhost. 
Devices *that are on your local network* are able to detect your host system IP and display the UI.
Virtual machines will generally also be able to pinpoint your development instance by IP.

**Set it up**

First, find your host system IP address on your local network. 
There are various ways to do this depending on your system. 
Your IP could be something like ``10.0.0.23``

Open ``/docker-compose.yml`` and find the following bit of text::

  environment:
    - SIMPLESAMLPHP_BASEURLPATH=http://localhost:8080/simplesaml/
    - SIMPLESAMLPHP_SP_ENTITY_ID=http://localhost:8080
    - SIMPLESAMLPHP_SP_ASSERTION_CONSUMER_SERVICE=http://localhost:8080/api/saml2_auth/acs/

Replace all mentions of *localhost* with your IP like this::

  environment:
    - SIMPLESAMLPHP_BASEURLPATH=http://10.0.0.23:8080/simplesaml/
    - SIMPLESAMLPHP_SP_ENTITY_ID=http://10.0.0.23:8080
    - SIMPLESAMLPHP_SP_ASSERTION_CONSUMER_SERVICE=http://10.0.0.23:8080/api/saml2_auth/acs/

Open ``/dev-environment/dev-settings.ini`` and find the following bit of text::

  ALLOWED_HOSTS=localhost,bev

Add your IP to the line like this::

  ALLOWED_HOSTS=localhost,bev,10.0.0.23

In the command line, kill and reboot your development instance to use the new configuration.
First with CTRL+C and then::

  docker-compose down -v
  docker-compose up

You should now be able to point a browser in your VM or mobile device to ``10.0.0.23:8080`` and see the frontend working.


Tutorial: Change the logo
-------------------------

This tutorial will give you a simple introduction to customizing the frontend for your own purposes.

Say, you want to change the logo image that rests in the top left corner of every page. 
You'll need to do the following:

# Add a new image to the frontend source files
# Identify the component that displays the logo
# Edit the corresponding template and maybe add some styles
# Build the frontend

Let's go through these steps in greater detail.


Add a new image
^^^^^^^^^^^^^^^

Static resources like images, icons, and multimedia are found in the ``/frontend/public`` folder. 

If you look inside the folder, you'll find a *logo.png* file in there already. 
Now you could easily swap it for a different image with the same filename but that's no fun. 
Instead, get a new *my-logo.png* image and drop it into ``/fontend/public``.


Find the component that displays the logo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You probably saw an *index.html* file while looking into the ``/fontend/public`` folder.
It doesn't contain much of interest since all of the references to javascript and css files are created in the build step.
But if you want to add external stylesheets or a new favicon, this *index.html* is the place to do it.

The real heart of our single page application is in ``/frontend/src/App.vue``
All the dynamically generated views are piped into *App.vue*.
If you open the file, you'll see a ``<template>`` section, a ``<script>`` section, and a ``<style>`` section.
These are typical sections in a Vue component file.

Notice the line with ``<router-view v-if="auth" />`` in the ``<template>`` section. 
The *router-view* element is the entrypoint for Vue Router to pipe ind content. 
When you navigate between views in the single page application, it's really just the contents of *router-view* that are being swapped.
Looking into ``/frontend/src/router.js`` will tell you what components are displayed for each route.
This is a good starting point for understanding what components are being displayed at any given time.

**But** since the logo is present on every page, it is not displayed using *router-view*.
The logo resides in the header so you must look into ``<app-header />``.
If you read about `vue components <https://vuejs.org/v2/guide/components.html>`_, you'll know that this element corresponds to the *import* statement in the ``<script>`` section that references ``/frontend/src/components/header/Header.vue``
Opening *Header.vue* will show you where the logo image is integrated.


Edit template
^^^^^^^^^^^^^

In *Header.vue* you'll find that the logo is found in this line ``<img class="global-logo" src="/logo.png" alt="">``.
Change the *src* attribute of the *img* element to "/my-logo.png".
Notice that the image src URL considers ``/frontend/public`` folder to be the root folder for static files. 
So the proper way to point to ``/frontend/public/my-logo.png`` is to enter ``/my-logo.png``.

Maybe your new logo has some different dimensions so you might want to change the logo's styles.
The *img* element has class *global-logo*. 
Look in the ``<styles>`` section of *Header.vue* to find the CSS rules for ``.global-logo`` and change it accordingly.
Styles that only apply to a certain component are usually added directly to Vue components like this.
Global styles are added in *App.vue* or in some of the CSS files in ``/frontend/src/assets/css``


Build the frontend
^^^^^^^^^^^^^^^^^^

If you are running in development mode, your changes should display in the browser right after you save your changes.
For a production build, you'd run the ``npm run build`` command and host the built files from ``/frontend/dist`` somewhere.
Now you've customized the frontend :)
