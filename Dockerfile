FROM kitware/trame

EXPOSE 80

COPY --chown=trame-user:trame-user ./deploy /deploy
COPY --chown=trame-user:trame-user . /local-app

RUN /opt/trame/entrypoint.sh build
