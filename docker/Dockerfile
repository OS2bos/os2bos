FROM node:10 AS frontend

WORKDIR /code/frontend

COPY frontend/package.json .
COPY frontend/package-lock.json .
# We fail hard if the yaml.lock is outdated.
RUN npm install --frozen-lockfile

COPY frontend .
RUN npm run build

CMD npm run serve


# We do not use alpine. The resulting image is smaller, but there is currently
# no support for pip installation of wheels (binary) packages. It falls back to
# installing from source which is very time consuming. See
# https://github.com/pypa/manylinux/issues/37 and
# https://github.com/docker-library/docs/issues/904
#
# We also don't use -slim as some python packages are not wheels and needs
# compiling with the tools from the non -slim image.
FROM python:3.7 AS dist


LABEL org.opencontainers.image.title="Bevillingsplatform" \
      org.opencontainers.image.vendor="Magenta ApS" \
      org.opencontainers.image.licenses="MIT"
      #org.opencontainers.image.url="" \
      #org.opencontainers.image.documentation="" \
      #org.opencontainers.image.source=""


# Force the stdout and stderr streams from python to be unbuffered. See
# https://docs.python.org/3/using/cmdline.html#cmdoption-u
ENV PYTHONUNBUFFERED=1 \
  BEV_SYSTEM_CONFIG_PATH=/code/docker/docker-settings.ini \
  BEV_USER_CONFIG_PATH=/user-settings.ini \
  IPYTHONDIR=/tmp/.ipython


WORKDIR /code/
COPY backend/sys-requirements.txt sys-requirements.txt
RUN set -ex \
  # Add a bev group and user. Note: this is a system user/group, but have
  # UID/GID above the normal SYS_UID_MAX/SYS_GID_MAX of 999, but also above the
  # automatic ranges of UID_MAX/GID_MAX used by useradd/groupadd. See
  # `/etc/login.defs`. Hopefully there will be no conflicts with users of the
  # host system or users of other docker containers.
  #
  # See `doc/user/installation.rst` for instructions on how to overwrite this.
  && groupadd -g 72050 -r bev\
  && useradd -u 72050 --no-log-init -r -g bev bev \
  # Install system dependencies from file.
  && apt-get -y update \
  && apt-get -y install --no-install-recommends $(grep -vE "^\s*#" sys-requirements.txt  | tr "\n" " ") \
  # clean up after apt-get and man-pages
  && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/man/?? /usr/share/man/??_* \
  # create folders at easily mountable paths for output from django
  && install -o bev -g bev -d /static \
  && install -o bev -g bev -d /log


# Install requirements
COPY backend/requirements.txt /code/backend/requirements.txt
COPY backend/requirements-test.txt /code/backend/requirements-test.txt
RUN pip3 install -r backend/requirements.txt -r backend/requirements-test.txt


# Copy and install backend code.
COPY README.md .
COPY LICENSE .
COPY docker ./docker
COPY tox.ini .
COPY backend ./backend

# Copy frontend code.
COPY --from=frontend /code/frontend/package.json ./frontend/package.json
COPY --from=frontend /code/frontend/dist ./frontend/dist

# Run the server as the bev user on port 5000
WORKDIR /code/backend
USER bev:bev
EXPOSE 5000
ENTRYPOINT ["/code/docker/docker-entrypoint.sh"]
CMD ["gunicorn", \
  "--config", "/code/docker/gunicorn-settings.py", \
  "bevillingsplatform.wsgi"]
