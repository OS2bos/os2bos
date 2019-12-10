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
When you edit files located in ``/frontend/src``, Vue CLI server uses hot relead to immediately reload the changes in your browser.

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


Hacking
-------


Styling
-------


Parts overview
--------------


Documentation outline:
----------------------

* Getting started
* Building for production
* Building for development
* Working with styles
* Working with views
* Working with vue-router
* working with vuex

* Usable modules: Store modules, mixins, filters