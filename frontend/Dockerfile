FROM node:22-alpine AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install

COPY . .
ARG PUBLIC_API_BASE_URL=http://localhost:8080
ENV PUBLIC_API_BASE_URL=$PUBLIC_API_BASE_URL
RUN npm run build

FROM node:22-alpine

WORKDIR /app
ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=3000

COPY --from=build /app/build ./build
COPY --from=build /app/package.json ./
COPY --from=build /app/package-lock.json ./
RUN npm install --omit=dev

EXPOSE 3000
CMD ["node", "build/index.js"]
