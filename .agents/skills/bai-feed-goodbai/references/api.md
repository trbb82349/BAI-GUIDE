# BAI Feed API Reference

Base URL defaults to `https://bai.haiinu.com`.

## Login Auth

POST `/api/login`

```json
{
  "name": "...",
  "password": "..."
}
```

Success creates a Flask session cookie.

POST `/api/web/post`

```json
{
  "did": "...",
  "learned": "...",
  "blocked": "...",
  "tags": "...",
  "links": "...",
  "project_id": null
}
```

Success returns:

```json
{
  "id": 123,
  "url": "/post/123"
}
```

## API Key Auth

POST `/api/post`

This is the preferred automation endpoint for `/goodbai`.

Header:

```text
X-API-Key: ...
```

Payload is the same as `/api/web/post`.

## Projects

GET `/api/projects` requires login. MVP keeps `project_id` as `null` unless an exact id is already known. A later version can login, fetch active projects, and select by project title.
