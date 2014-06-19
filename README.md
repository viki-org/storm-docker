About this branch
=================

This is used to generate the `gh-pages` branch we see on
http://dev.viki.com/storm-docker/

## Development

Run:

    script/server

This will watch for changes, including for sass files.

## Building

    ./build.sh

This creates a `_site` directory, whose contents are ready to be committed to
the master branch.
