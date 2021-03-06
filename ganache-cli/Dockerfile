# node:alpine will be our base image to create this image
FROM node:alpine

ARG WEB3_FORK_URL
ENV WEB3_FORK_URL ${WEB3_FORK_URL}

# Set the /app directory as working directory
WORKDIR /app

# Install ganache-cli globally
RUN npm install -g ganache-cli

EXPOSE 8545

# Set the default command for the image
CMD ganache-cli -h 0.0.0.0 --fork ${WEB3_FORK_URL}
