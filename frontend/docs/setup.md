# Installation and setup

If you have [docker](https://www.docker.com/) installed and followed the [installation instructions](../README.md) , you already have the frontend up and running.

Open your browser and point to `localhost:8080` to see the GUI in action. 
You should be able to log in with username **admin** and password **admin**.

In this configuration, the frontend lives inside a docker container running the Vue CLI server. 
When you edit files located in `/frontend/src`, Vue CLI server uses hot reload to immediately reload the changes in your browser.

**Note:** This setup is only suitable for development use. You should make a proper production build for any public use.


## Building

**In development mode,** the frontend is hosted inside a docker container running Vue CLI. 
**In production mode,** you don't need this since you just need to host the bundled javascript and CSS files.

To access the docker container, run `docker exec -it bevillingsplatform_frontend_1 bash` from the project root on your host machine.
Now you can run various commands using [npm](https://docs.npmjs.com/)


### Building for development

Run `npm run serve` inside the frontend docker container to start Vue CLI. 
You rarely need to do this since Vue CLI starts as soon as the container is initiated.


### Building for production

Run `npm run build` inside the frontend docker container to create a production build.
If the build is successful, you'll find the finished bundle in the `/frontend/dist` folder.
