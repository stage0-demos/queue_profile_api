# Sample API

## Prerequisites
- Mentor Hub [Developers Edition](https://github.com/agile-learning-institute/mentorhub/blob/main/CONTRIBUTING.md)
- Developer [API Standard Prerequisites](https://github.com/agile-learning-institute/mentorhub/blob/main/DeveloperEdition/standards/api_standards.md)

## Developer Commands

```bash
## Install dependencies
pipenv install

# start backing db container 
# Container Related commands use `de down` before starting the requested containers
pipenv run db

## run unit tests 
pipenv run test

## run api server in dev mode - captures command line, serves API at localhost:8389
pipenv run dev

## run E2E tests (assumes running API at localhost:8389)
pipenv run e2e

## run tests with coverage report
pipenv run coverage

## build application (pre-compiles Python code)
pipenv run build

## build container 
pipenv run container

## Run the backing database and api containers
pipenv run api

## Run the full microservice (db+api+spa)
pipenv run service

## format code
pipenv run format

## lint code
pipenv run lint
```

## Project Structure

- `src/` - Main package containing:
  - `server.py` - API entrypoint
  - `routes/` - HTTP request/response handlers
  - `services/` - Business logic and RBAC

- `test/` - Test suite with matching directory structure:
  - `routes/` - Route unit tests
  - `services/` - Service unit tests
  - `e2e/` - End-to-end tests flagged with `@pytest.mark.e2e`

## API Endpoints

see the [Open API Specifications](./docs/openapi.yaml) for details on the API

### Simple Curl Commands:
```bash
# Get a token
export TOKEN=$(curl -s -X POST http://localhost:8389/dev-login \
  -H "Content-Type: application/json" \
  -d '{"subject": "user-123", "roles": ["admin"]}' | jq -r '.access_token')

# Get the API Configuration
curl http://localhost:8389/api/config \
  -H "Authorization: Bearer $TOKEN"

```