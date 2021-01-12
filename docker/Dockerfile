# alpine is a lightweight OS for creating dockerize app
FROM python:3.8.2-alpine

# Ensuring we can see log reports on our console without buffer hold back
ENV PYTHONUNBUFFERED 1

# This will enable scripts to be added to the running container
ENV PATH="/scripts:${PATH}"

# Upgrade pip
RUN pip install --upgrade pip

# This will copy our requirements file to the docker image
COPY ../requirements/production.txt /requirements.txt

# Required packages to run on alpine use to install the uWSGI server
# Update -- package repository to be updated when this command is run
# cache -- no storing of cache when the update runs, keeping the container lightweight
# virtual .tmp -- To remove the dependencies after .tmp when we are done with them
# gcc libc-dev linux-headers -- needed to install the requirements.txt
RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers

# Install postgres dependencies for your app
RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

# Installing pillow depencies
RUN apk add --no-cache  zlib-dev jpeg-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev gcc musl-dev

# Installing cffi dependencies
RUN apk add libffi-dev py-cffi

# Installing lxml dependencies
RUN apk add libxml2-dev libxslt-dev

# Add postgres client
RUN apk add postgresql-client

# Install the project dependencies
RUN pip install -r /requirements.txt --no-cache-dir

# remove the dependencies after .tmp & .build-deps since we don't need them to install our req.txt file again,
# keeping the container lightweight
RUN apk del .tmp
RUN  apk --purge del .build-deps

# Create a new app directory in the root of our dockerfile
RUN mkdir /app

# Copy contents of your project app to the above created app
copy ./locallibrary /app

# Change the working directory to the created app which contains our django project
WORKDIR /app

# Copy Scripts file thats is useful for our docker image
COPY ../../scripts /scripts

# Add the correct executable permission to the created scripts
# Any scripts added to the folder gets the executable permission
RUN chmod +x /scripts/*

# creating two new directories in our docker image for our static files and media
RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

# Create a new user in the image to run the application, AVOID using the root user to run the
# application. If the container gets compromised, it minimise the access an attacker could get
# for when app the is comprmoised
RUN adduser -D user

# Set the owner of the vol directory to the user just created, this is so, so that the application
# running would have permission to access to the directory
RUN chown -R user:user /vol

# Give the user full access and the groups and everyone else has read access
RUN chmod -R 755 /vol/web

# switch to the created user
USER user

# Command for the entry point to the application in production
CMD ["entrypoint.sh"]
