FROM python:3.11-alpine

LABEL maintainer="fengwm64 <fengwm64@163.com>"

WORKDIR /app

COPY ./requirements.txt .

# apk repository
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories

# timezone and dependencies
RUN apk add --no-cache tzdata libxml2 libxslt \
    && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del tzdata

COPY . .

EXPOSE 5010

CMD ["sh", "start.sh"]
