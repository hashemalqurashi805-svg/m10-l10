# المرحلة الأولى: البناء (builder)
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# إضافة أمر لإنشاء المجلد إذا لم يكن موجوداً
RUN mkdir -p public
RUN npm run build

# المرحلة الثانية: التشغيل (runner)
FROM node:18-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
# الآن لن يظهر خطأ لأن المجلد موجود حتماً
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["npm", "start"]