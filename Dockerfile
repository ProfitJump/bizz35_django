# Pull base image
ARG ARCH=arm64
# AlpineLinux with a glibc-2.29-r0 and python3
FROM --platform=linux/${ARCH} alpine:3.18
ARG ARCH
#ENV ARCH=$(cat "$ARCH" | sed -e 's/ \/  //'    )
ENV ARCH=$ARCH

RUN set -ex && \
   echo $ARCH | sed -e 's/\///'  > /etc/ARCH

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies
COPY ./requirements.txt .
RUN set -ex && \ pip install -r requirements.txt

# Copy project
COPY . .