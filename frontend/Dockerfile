# 베이스 이미지는 node:lts-alpine (가볍고 빠름)
FROM node:lts-alpine AS build

# pnpm 설치
RUN npm install -g pnpm

# 작업 디렉토리 생성
WORKDIR /app

# 의존성 설치 및 빌드
COPY package.json pnpm-lock.yaml ./
RUN pnpm install

COPY . .
RUN pnpm build

# --------------------------------------------

# 실제 운영용 컨테이너는 nginx 사용
FROM nginx:stable-alpine

# nginx.conf 설정 복사 (없으면 기본 설정 사용)
# COPY nginx.conf /etc/nginx/nginx.conf

# 빌드 결과를 nginx static 폴더로 복사
COPY --from=build /app/dist /usr/share/nginx/html

# 포트 80으로 노출
EXPOSE 80

# nginx 실행
CMD ["nginx", "-g", "daemon off;"]
