#FROM node:6.11.0-alpine
FROM node:4.8.2-alpine

RUN apk update
RUN apk add paxctl
RUN paxctl -cm /usr/local/bin/node
# Oddly, node-sass requires both python and make to build bindings
RUN apk add python make g++
# Install gulp globally so it can be used during builds
RUN npm install --global gulp-cli
