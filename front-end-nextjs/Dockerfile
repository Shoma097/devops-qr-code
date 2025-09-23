FROM node:18-alpine AS base

WORKDIR /app

COPY package.json package-lock.json* pnpm-lock.yaml* ./
RUN \
    if [ -f package-lock.json ]; then npm install --prefer-offline; \
    elif [ -f pnpm-lock.yaml ]; then npm install -g pnpm && pnpm install --prefer-offline; \
    else npm install --prefer-offline; \
    fi

COPY . .

RUN npm run build

EXPOSE 3000

CMD [ "npm" , "start"]