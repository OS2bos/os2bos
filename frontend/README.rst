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
You should be able to log in with username **admin** and password **sagsbehandler**.

In this configuration, the frontend lives inside a docker container running the Vue CLI server. 
When you edit files located in ``/frontend/src``, Vue CLI server uses hot relead to immediately reload the changes in your browser.

**Note:** This setup is only suitable for development use.


Building
--------


Testing
-------

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