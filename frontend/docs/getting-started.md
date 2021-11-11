# Getting started

This is a tutorial which will give you a simple introduction to customizing the frontend for your own purposes.

Say, you want to change the logo image that rests in the top left corner of every page. 
You'll need to do the following:

1. Add a new image to the frontend source files
2. Identify the component that displays the logo
3. Edit the corresponding template and maybe add some styles
4. Build the frontend

Let's go through these steps in greater detail.


## Add a new image

Static resources like images, icons, and multimedia are found in the `/frontend/public` folder. 

If you look inside the folder, you'll find a *logo.png* file in there already. 
Now you could easily swap it for a different image with the same filename but that's no fun. 
Instead, get a new *my-logo.png* image and drop it into `/fontend/public`.


## Find the component that displays the logo

You probably saw an `index.html` file while looking into the `/fontend/public` folder.
It doesn't contain much of interest since all of the references to javascript and css files are created in the build step.
But if you want to add external stylesheets or a new favicon, this `index.html` is the place to do it.

The real heart of our single page application is in `/frontend/src/App.vue`
All the dynamically generated views are piped into `App.vue`.
If you open the file, you'll see a `<template>` section, a `<script>` section, and a `<style>` section.
These are typical sections in a Vue component file.

Notice the line with `<router-view v-if="auth" />` in the `<template>` section. 
The **router-view** element is the entrypoint for Vue Router to pipe ind content. 
When you navigate between views in the single page application, it's really just the contents of **router-view** that are being swapped.
Looking into `/frontend/src/router.js` will tell you what components are displayed for each route.
This is a good starting point for understanding what components are being displayed at any given time.

**But** since the logo is present on every page, it is not displayed using **router-view**.
The logo resides in the header so you must look into `<app-header />`.
If you read about [vue components](https://vuejs.org/v2/guide/components.html), you'll know that this element corresponds to the _import_ statement in the `<script>` section that references `/frontend/src/components/header/Header.vue`
Opening `Header.vue` will show you where the logo image is integrated.


## Edit template

In `Header.vue` you'll find that the logo is found in this line `<img class="global-logo" src="/logo.png" alt="">`.
Change the _src_ attribute of the `img` element to "/my-logo.png".
Notice that the image src URL considers `/frontend/public` folder to be the root folder for static files. 
So the proper way to point to `/frontend/public/my-logo.png` is to enter `/my-logo.png`.

Maybe your new logo has some different dimensions so you might want to change the logo's styles.
The `img` element has class _global-logo_. 
Look in the `<styles>` section of `Header.vue` to find the CSS rules for `.global-logo` and change it accordingly.
Styles that only apply to a certain component are usually added directly to Vue components like this.
Global styles are added in `App.vue` or in some of the CSS files in `/frontend/src/assets/css`


## Build the frontend

If you are running in development mode, your changes should display in the browser right after you save your changes.
For a production build, you'd run the `npm run build` command and host the built files from `/frontend/dist` somewhere.
Now you've customized the frontend :)
