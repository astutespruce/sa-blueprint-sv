FROM node:14-buster-slim

# install required libGL.so.1 for cwebp
RUN apt update && apt install -y libgl1-mesa-glx libxi6

RUN npm install -g gatsby-cli && gatsby telemetry --disable

WORKDIR /app
COPY ./ui/package*.json ./
RUN npm ci
