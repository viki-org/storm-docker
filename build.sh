#!/bin/bash

set -e

rm -rf _site
jekyll build
rm _site/build.sh _site/config.rb _site/Gemfile _site/Gemfile.lock \
  _site/Procfile _site/README.md _site/stylesheets/*.scss
rm -rf _site/script
