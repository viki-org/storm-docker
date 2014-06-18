About this branch
=================

This is used to generate the `gh-pages` branch we see on
http://dev.viki.com/storm-docker/

## Development

    bundle exec middleman server

Once you have a browser accessing the page, live reload is done on the browser
upon any saved changes.

## Building

    bundle exec middleman build

This builds everything in a `build` folder. The files inside the `build` folder
are what we commit to the `gh-pages` branch.
