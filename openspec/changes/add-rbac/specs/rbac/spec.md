## Purpose

Controls who may perform privileged operations and see sensitive UI by assigning each user a role that carries a set of permissions.

## ADDED Requirements

### Requirement: Seeded roles and permissions

The system SHALL persist roles and permissions and SHALL seed `admin`, `manager`, and `member` roles on startup if they are missing. New and self-registered users MUST be assigned the `member` role. The first configured administrator account MUST be assigned the `admin` role.

Seeded permission codes MUST be:

- `users:list` — list all users, or view a user other than yourself
- `users:create` — create a user
- `users:manage` — update or delete a user other than yourself
- `metrics:view` — view the metrics/insights page
- `system:admin` — catch-all for remaining admin-only surfaces (item access across all owners, transactional-email test/preview endpoints); also the permission that blocks self-deletion

Role grants MUST be:

| Role      | `users:list` | `users:create` | `users:manage` | `metrics:view` | `system:admin` |
|-----------|:---:|:---:|:---:|:---:|:---:|
| `admin`   | ✓ | ✓ | ✓ | ✓ | ✓ |
| `manager` | ✓ |   |   | ✓ |   |
| `member`  |   |   |   |   |   |

#### Scenario: Fresh database has default roles

- **WHEN** the application initializes an empty database
- **THEN** roles `admin`, `manager`, and `member` exist; `admin` holds all seeded permission codes; `manager` holds `users:list` and `metrics:view`; `member` holds none

#### Scenario: Self-registration gets the default role

- **WHEN** a visitor registers a new account
- **THEN** that account is assigned the `member` role

#### Scenario: First administrator is an admin

- **WHEN** the configured first administrator account is created
- **THEN** that account is assigned the `admin` role

### Requirement: One role per user

Each user MUST have exactly one role. An authorized administrator MUST be able to assign an existing role when creating or updating another user. The API MUST NOT accept `is_superuser`. User representations MUST include the user's role identifier (slug).

#### Scenario: Admin assigns the manager role

- **WHEN** a caller with `users:create` creates a user with role `manager`
- **THEN** that user is stored with the `manager` role

#### Scenario: Superuser field is rejected

- **WHEN** a client sends `is_superuser` on a user create or update payload
- **THEN** the field is not part of the public contract and does not grant privileges

### Requirement: Current user exposes permissions

`GET` current-user MUST return the authenticated user's role slug and the list of permission codes granted by that role.

#### Scenario: Admin current user payload

- **WHEN** an `admin` user requests their own profile
- **THEN** the response includes role `admin` and every seeded permission code

#### Scenario: Manager current user payload

- **WHEN** a `manager` user requests their own profile
- **THEN** the response includes role `manager` and permissions `users:list` and `metrics:view` only

#### Scenario: Default member current user payload

- **WHEN** a `member`-role user requests their own profile
- **THEN** the response includes role `member` and an empty permission list

### Requirement: API enforces permissions

Sensitive endpoints MUST require the matching permission and MUST respond with HTTP 403 when the caller lacks it. Authentication is still required as today. Viewing and updating **your own** profile MUST always succeed for any authenticated, active user regardless of role — it requires no permission.

| Permission | Protected operations |
|---|---|
| `users:list` | List all users; get a user other than yourself by id |
| `users:create` | Create a user |
| `users:manage` | Update or delete a user other than yourself |
| `metrics:view` | View the metrics/insights endpoint and page |
| `system:admin` | Read or write items the caller does not own; transactional-email test/preview endpoints; required to be absent for self-delete to succeed |

#### Scenario: Manager can list users but not create one

- **WHEN** a `manager` requests the user list
- **THEN** the API returns 200
- **WHEN** that same `manager` attempts to create a user
- **THEN** the API returns 403

#### Scenario: Member cannot list users or view metrics

- **WHEN** a `member` requests the user list or the metrics endpoint
- **THEN** the API returns 403 for both

#### Scenario: Manager can view metrics

- **WHEN** a `manager` requests the metrics endpoint
- **THEN** the API returns 200

#### Scenario: Any authenticated user can update their own profile

- **WHEN** a `member` updates their own profile via the current-user endpoint
- **THEN** the update succeeds

#### Scenario: Manager cannot update another user's profile

- **WHEN** a `manager` (who lacks `users:manage`) attempts to update a different user's profile
- **THEN** the API returns 403

#### Scenario: Owner can still manage own item

- **WHEN** a caller without `system:admin` updates an item they own
- **THEN** the update succeeds

#### Scenario: Non-owner cannot update another's item

- **WHEN** a caller without `system:admin` updates an item they do not own
- **THEN** the API returns 403

#### Scenario: Admin cannot self-delete

- **WHEN** a user whose role includes `system:admin` requests deletion of their own account
- **THEN** the API returns 403

### Requirement: UI gates sensitive sections

The web app MUST hide navigation and routes that require a permission the current user does not have. Admin user-management UI MUST be reachable only with `users:list` (view) and MUST use role assignment instead of a superuser checkbox, offering all three seeded roles. The metrics/insights page MUST be reachable only with `metrics:view`. Users without `system:admin` MUST still be offered account self-deletion in settings; users with `system:admin` MUST NOT.

Direct navigation to a route the current user lacks permission for MUST show a friendly "Access Denied" page explaining the user lacks permission — never a silent redirect, a blank page, or a cryptic error.

#### Scenario: Member sees no admin or metrics nav items

- **WHEN** a `member` is signed in
- **THEN** neither the admin nav item nor the metrics nav item is shown in the sidebar

#### Scenario: Member navigating directly to admin or metrics sees Access Denied

- **WHEN** a `member` navigates directly to the admin users page or the metrics page by URL
- **THEN** the app shows a friendly "Access Denied" page instead of the requested content, a silent redirect, or a cryptic error

#### Scenario: Manager can open user management but not create a user

- **WHEN** a `manager` opens the admin users page
- **THEN** the page loads with users shown, but no control to create a user is offered

#### Scenario: Manager can open the metrics page

- **WHEN** a `manager` opens the metrics page
- **THEN** the page loads

### Requirement: Existing superusers migrate to admin

On schema migration, every user with `is_superuser` true MUST receive the `admin` role and every other user MUST receive the `member` role. The `is_superuser` column MUST be removed.

#### Scenario: Legacy superuser becomes admin

- **WHEN** the RBAC migration runs against a database that has a superuser
- **THEN** that user has the `admin` role after migration and `is_superuser` no longer exists

#### Scenario: Legacy non-superuser becomes a member

- **WHEN** the RBAC migration runs against a database that has a non-superuser
- **THEN** that user has the `member` role after migration
