FROM python:3.11-slim

WORKDIR /app

# copy application files from ../app into image
COPY ../app/ /app/

# install dependencies if requirements.txt exists
RUN pip install --no-cache-dir -r /app/requirements.txt
# copy the entrypoint script from the project config into the image
# (Dockerfile is in backend/docker, so ../config points to backend/config)
COPY ../config/entrypoint.sh /config/entrypoint.sh

# ensure the entrypoint is executable and expose the default port
RUN chmod +x /config/entrypoint.sh
EXPOSE 8000

ENTRYPOINT ["/config/entrypoint.sh"]