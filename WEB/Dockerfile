FROM node:20.3.1

COPY package.json package-lock.json ./
RUN npm install 
COPY . ./

ENTRYPOINT ["npm", "start"]