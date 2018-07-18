#!/bin/bash

for i in {1..12}
do
  wget -q https://swgoh.gg/static/img/ui/gear-icon-g$i.svg
  convert -size 128x128 -background transparent gear-icon-g$i.svg gear-icon-g$i.png
  rm gear-icon-g$i.svg
done
