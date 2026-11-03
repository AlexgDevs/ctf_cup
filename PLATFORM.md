---
name: biba-platform
description: Use when interacting with the biba CTF platform: listing tasks, reading task attachments, fetching the user profile and running instances, extending instances, or submitting flags. Covers token acquisition, request formats, instance connection methods, and the end-to-end task workflow.
---

# biba CTF Platform Interaction

This skill is for interacting with the biba CTF platform. It describes the API, request and response formats, when to call each method, and how to connect to task instances. It is not a guide for solving the challenges themselves.

## Platform addresses

All paths below are relative to these base URLs:

```text
API_BASE_URL      = https://api.ctfcup.online
PLATFORM_BASE_URL = https://ctfcup.online
```

- `API_BASE_URL` serves the authenticated API (`/api/*`).
- `PLATFORM_BASE_URL` serves static files, task attachments, and the read-only platform API (`/platform/*`).

## Authentication token

Ask the user to:

1. Log in to the platform in a browser.
2. Open the browser developer console.
3. Run:

```js
console.log(localStorage.getItem('session.token'))
```

4. Paste the printed token into the chat.

Use the token only in request bodies. Do not write it to files, print it back, or include it in reports. Treat it as a full account session.

If any authenticated request returns `401 Unauthorized`, ask the user to log in again and provide a fresh token.

Every authenticated request uses this JSON envelope:

```json
{
  "session": {
    "token": "<TOKEN>"
  }
}
```

All API requests use `Content-Type: application/json` and must be sent with `POST`.

## Endpoints

### GET /platform/info

No authentication.

Returns the current game information. Relevant fields:

```json
{
  "start_time": "2026-10-30T15:00:00+03:00",
  "finish_time": "2026-10-30T23:59:59+03:00",
  "captcha_required": true,
  "confirmation_required": true,
  "registration_enabled": false,
  "scoring_type": "dynamic",
  "websocket_endpoint": "wss://..."
}
```

Use it to check whether the game has started and is still running.

### GET /platform/tasks

No authentication.

Returns the list of tasks:

```json
[
  {
    "id": "task-id",
    "type": "static",
    "title": "Task title",
    "description": "Markdown description",
    "min_price": 100,
    "max_price": 1000,
    "tags": ["pwn"],
    "attachments": ["attachments/abc/task.tar.gz"],
    "flag_format": "ctf{...}",
    "created_at": "2026-10-30T12:00:00+03:00"
  }
]
```

Task types:

- `static` â€” no instance; solve from the description and attachments.
- `http` â€” instance provides a ready HTTP endpoint.
- `tcp` â€” instance provides a TCP endpoint and a token to send after connecting.
- `ssh` â€” instance provides an SSH endpoint; the token is the SSH username.

Attachments are relative paths. Download them from:

```text
{PLATFORM_BASE_URL}/{attachment}
```

Example:

```text
https://example.org/attachments/abc/task.tar.gz
```

### POST /api/users/profile

Authentication required.

Request:

```json
{
  "session": {
    "token": "<TOKEN>"
  }
}
```

Response:

```json
{
  "user": {
    "user_id": 123,
    "username": "player",
    "email": "player@example.org",
    "from": 1,
    "comment": "...",
    "created_at": "2026-01-01T00:00:00Z"
  },
  "instances": [
    {
      "type": "tcp",
      "task_id": "task-id",
      "token": "FB4FU4V6TITJRCOLERUJC9X0WLJCYYPN",
      "endpoint": "nc instance.host 1337",
      "created_at": "2026-10-30T15:00:00+03:00",
      "expire_at": "2026-10-30T16:00:00+03:00"
    }
  ]
}
```

Use this endpoint to validate the token and to find running instances.

The `endpoint` field is the ready-to-use connection string. Use it exactly as returned.

### POST /api/tasks/spawn

Authentication and captcha required.

**Do not call this endpoint.** The platform always requires a captcha for spawning, and the agent cannot obtain a valid captcha token.

Ask the user to spawn the instance from the platform UI in the browser. After the user confirms, call `/api/users/profile` until the instance for the requested `task_id` appears.

For reference, the request shape is:

```json
{
  "session": {
    "token": "<TOKEN>"
  },
  "captcha": {
    "token": "<CAPTCHA_TOKEN>"
  },
  "task_id": "task-id"
}
```

Response:

```json
{
  "instance": {
    "type": "tcp",
    "task_id": "task-id",
    "token": "FB4FU4V6TITJRCOLERUJC9X0WLJCYYPN",
    "endpoint": "nc instance.host 1337",
    "created_at": "2026-10-30T15:00:00+03:00",
    "expire_at": "2026-10-30T16:00:00+03:00"
  }
}
```

### POST /api/tasks/extend

Authentication required. No captcha.

Request:

```json
{
  "session": {
    "token": "<TOKEN>"
  },
  "task_id": "task-id"
}
```

Response:

```json
{
  "expire_at": "2026-10-30T17:00:00+03:00"
}
```

Use this while solving a long challenge when the current instance is close to expiring. Update the known `expire_at` from the response.

Possible errors:

- `instance not found` â€” the instance is already gone; ask the user to spawn a new one.
- `game is not running` â€” the game window is closed.

### POST /api/tasks/submit

Authentication required.

Request:

```json
{
  "session": {
    "token": "<TOKEN>"
  },
  "task_id": "task-id",
  "flag": "ctf{...}"
}
```

Success returns an empty JSON object.

Possible errors:

- `invalid flag` â€” the flag is wrong; continue solving.
- `task already solved` â€” the task is already submitted.
- `game is not running` â€” submission is no longer allowed.

Do not brute-force or repeatedly submit guesses.

### POST /api/tasks/destroy

Authentication required.

**Do not call this endpoint.** After the task is completed, ask the user to destroy the instance from the platform UI.

For reference, the request shape is:

```json
{
  "session": {
    "token": "<TOKEN>"
  },
  "task_id": "task-id"
}
```

## Instance connection methods

Use the `endpoint` returned by `/api/users/profile` exactly as provided.

### HTTP

The endpoint is a complete URL:

```text
http://rdophcd809eix2g1.instance.host
```

Use `curl`, a browser, or another HTTP client:

```sh
curl -v 'http://rdophcd809eix2g1.instance.host'
```

### TCP

The endpoint is a netcat-style command:

```text
nc instance.host 1337
```

Connect, wait for the token prompt, then send the instance `token` followed by a newline:

```text
[*] Please, enter token:
> FB4FU4V6TITJRCOLERUJC9X0WLJCYYPN
[+] Connecting...
```

The instance output follows after the connection is established.

### SSH

The endpoint contains the SSH username and host:

```text
ssh vxzc1eiwsn1vpex6@instance.host
```

No password is required. Use the endpoint directly:

```sh
ssh vxzc1eiwsn1vpex6@instance.host -- id
```

## Workflow

1. Ask the user for the session token.
2. Fetch `/platform/info` and `/platform/tasks`.
3. Find the requested task by id or title.
4. Check that the game has started and is still running.
5. Download and inspect the task attachments from `PLATFORM_BASE_URL` when needed.
6. If the task type is `static`, solve it and submit the flag.
7. If the task is dynamic:
   - Ask the user to spawn an instance for the task in the browser.
   - Poll `/api/users/profile` every 2â€“3 seconds until an instance with the requested `task_id` appears. Stop after about 60 seconds and ask the user to check the spawn.
   - Use the instance `endpoint` and `token` according to its type.
   - If the instance is close to expiring and the task is still being solved, call `/api/tasks/extend`.
   - Submit the found flag with `/api/tasks/submit`.
8. After successful submission, ask the user to destroy the instance from the platform UI.

## Error handling

- `401` â€” invalid or expired token; ask the user for a fresh token.
- `403` â€” the account is not allowed to perform the action; report it.
- `404` â€” the task or instance no longer exists.
- `game is not running` â€” stop and report that the game window is closed.
- `invalid flag` â€” keep solving; do not resend the same value.
- `task already solved` â€” report success and stop.
- `instance not found` â€” ask the user to spawn the instance again.

## Constraints

- Never call `/api/tasks/spawn` or `/api/tasks/destroy`.
- Never submit a flag unless it is believed to be correct.
- Never share or persist the session token.
- Poll the profile sparingly: every 2â€“3 seconds, not continuously.
