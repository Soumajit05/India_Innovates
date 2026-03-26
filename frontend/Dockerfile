FROM node:22-alpine

WORKDIR /app

COPY package.json ./
COPY tsconfig.json ./
COPY next-env.d.ts ./
COPY next.config.mjs ./
COPY postcss.config.js ./
COPY tailwind.config.ts ./

RUN npm install

COPY app ./app
COPY components ./components
COPY lib ./lib
COPY public ./public

EXPOSE 3000

CMD ["npm", "run", "dev"]
