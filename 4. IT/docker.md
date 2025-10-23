---
title: "docker"
created: 2024-03-15 13:09:52
updated: 2024-11-07 09:42:43
---
  * install
    * [홈페이지](docker.com)에서 install program download
  * 참고 사이트
    * https://tecoble.techcourse.co.kr/post/2022-09-20-docker-basic/
  * docker 구조 및 실행(build, pull, run)
    * Diagram
      * ![[100. media/image/FgVSABSxpW.png]]
    * docker file for node.js web application
      * ```plain text
# Use an official Node.js runtime as the base image
FROM node:14

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install application dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 3000

# Define the command to run the app
CMD ["node", "app.js"]```
    * build/run
      * ```shell
docker build -t my-nodejs-app
docker run -p 3000:3000 my-nodejs-app```
    * Scaling with docker
      * ```shell
docker run -d -p 3001:3000 my-nodejs-app
docker run -d -p 3002:3000 my-nodejs-app```