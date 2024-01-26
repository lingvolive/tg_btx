FROM python:3.9

#ARG FILE_PATH=files
#ARG APP_PATH=/opt/app
#ARG WOAR_APP_DIR=/opt/app/bitrix_bot

ARG APP_PATH
ARG WORK_APP_DIR
ARG PATH_FILES
ENV PATH_FILES      = ${PATH_FILES}
ENV DB_CONN_STR     = ${DB_CONN_STR}
ENV BOT_TOKEN         = ${BOT_TOKEN}
ENV BTX_URL_API_BATCH = ${BTX_URL_API_BATCH}
ENV ADMIN_PASSWORD    = ${ADMIN_PASSWORD}
ENV LANGUAGE          = ${LANGUAGE}
ENV TG_LOG_FILE_NAME  = ${TG_LOG_FILE_NAME}
ENV TG_LOG_LEVEL      = ${TG_LOG_LEVEL}
ENV TG_LOG_ROTATION_INTERVAL  = ${TG_LOG_ROTATION_INTERVAL}
ENV TG_LOG_FMT       = ${TG_LOG_FMT}
ENV TG_LOG_DATE_FMT  = ${TG_LOG_DATE_FMT}

COPY .   $APP_PATH
WORKDIR  $WORK_APP_DIR

RUN mkdir $PATH_FILES
RUN pip install -r requirements.txt
RUN apt-get update
#RUN apt-get install -y ffmpeg
#RUN apt-get install -y ffprobe

# expose port


# start app
CMD [ "python", "./main.py" ]
