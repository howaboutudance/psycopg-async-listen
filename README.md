# psycopg-async-listen

## Summary
`psycopg-async-listen` is a Python project that demonstrates using the `pyscopg3` library to add `NOTIFY` notifications
to a `asyncio.Queue` asynchrnously. 

## Setup Development Environment

### Prerequisites
- Python 3.12+
- `virtualenv`
- `docker` and `docker-compose` OR `podman` and `podman-compose`

### Steps

After cloning the repository:

1. (optional) setup pyenv to use a python ~= 3.12
    ```bash
    # set to the most recent 3.12 version installed
    pyenv local 3.12.6
    ```
2. Create and activate a virtual environment:
    ```bash
    virtualenv venv
    source venv/bin/activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running Unit Tests with Tox

2. Run the tests:
    ```bash
    tox -e py312
    ```

## Using Docker Compose and Running Integration Tests

1. Start the services (if using podman, repalce with podman-compose):
    ```bash
    docker-compose up -d
    ```

2. Setup the `./data/.pg_data` directory:
    ```bash
    mkdir -P data/.pg_data
    ```

3. Run the integration tests:
    ```bash
    tox -e integration
    ```

4. Stop the services:
    ```bash
    docker-compose down
    ```

## License
This project is licensed under the Apache 2.0 License.
