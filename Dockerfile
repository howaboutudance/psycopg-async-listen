# Use Fedora as the base image for building
FROM fedora:latest AS base
RUN dnf update -y && \
    dnf install -y python3 python3-pip && \
    pip install --root-user-action=ignore --upgrade pip && \
    adduser -m app 

# set python specfic environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PATH="venv/bin:$PATH"

FROM base AS build
# Set the working directory
WORKDIR /app
RUN chown -R app /app

# Copy the source code and configuration files
COPY ./src ./src
COPY pyproject.toml .env ./

# set user to app
USER app

# create a virtual environment and install the dependencies
# from the pyproject.toml file, DO NOT INSTALL POETRY!
RUN python -m venv .venv && \
    source ./.venv/bin/activate

USER root

# Build the packages into .whl files
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/dist . 

# Create a new stage for the application using a slim Python image
FROM base AS app

# Set the working directory
WORKDIR /app

# Copy the built .whl files from the build stage
COPY --from=build /app/dist /app/dist

RUN python -m venv .venv && \
    source ./.venv/bin/activate

USER app

# Install the .whl files
RUN pip install /app/dist/*

# Set the entrypoint
ENTRYPOINT ["python", "-m", "mqtt_publish"]

# Expose necessary ports (if any)
EXPOSE 1883