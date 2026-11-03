# Etapa builder: instala dependencias y produce el build de producción.
FROM node:22.22-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Etapa final: Nginx estático sirviendo el build de la SPA.
FROM nginx:1.30.6-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
