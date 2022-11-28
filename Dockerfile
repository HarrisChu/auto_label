FROM python:3.8.12-alpine AS builder
ADD . /app
WORKDIR /app

RUN apk add gcc linux-headers libc-dev libffi-dev
# We are installing a dependency here directly into our app source dir
RUN pip3 install --target=/app -r /app/requirements.txt

# A distroless container image with Python and some basics like SSL certificates
# https://github.com/GoogleContainerTools/distroless
FROM python:3.8.12-alpine
COPY --from=builder /app /app
WORKDIR /app
ENV PYTHONPATH /app
CMD ["python3", "/app/main.py"]
