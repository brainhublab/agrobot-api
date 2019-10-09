FROM python:3.7.4-alpine3.9
ENV PYTHONUNBUFFERED 1

RUN mkdir /usr/src/event_rules_storage_api

COPY . /usr/src/event_rules_storage_api

WORKDIR /usr/src/event_rules_storage_api/

RUN apk add --no-cache --virtual .build-deps \
    ca-certificates gcc postgresql-dev linux-headers musl-dev \
    libffi-dev jpeg-dev zlib-dev \
    && pip install -r requirements.txt \
    && find /usr/local \
        \( -type d -a -name test -o -name tests \) \
        -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
        -exec rm -rf '{}' + \
    && runDeps="$( \
        scanelf --needed --nobanner --recursive /usr/local \
                | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                | sort -u \
                | xargs -r apk info --installed \
                | sort -u \
    )" \
    && apk add --virtual .rundeps $runDeps \
    && apk del .build-deps

ENV LC_ALL=C.UTF-8
RUN export LANG=C.UTF-8
ENV FLASK_CONFIG=development
ENV FLASK_APP=run.py

RUN chmod +x ./run.sh && echo "$LC_ALL" && echo "$LANG" && echo "$FLASK_CONFIG" && echo "$FLASK_APP"

CMD ./run.sh

