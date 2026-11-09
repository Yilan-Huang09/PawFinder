# PawFinder Implementation Plan

> Design baseline: `docs/superpowers/specs/2026-11-09-pawfinder-design.md`

**Goal:** Deliver a locally runnable MySQL 8 + Flask + Vue 3 course project that demonstrates the complete lost-pet collaboration workflow, database objects, automated tests, and presentation-ready sample data.

**Architecture:** Vue 3 SPA calls a versioned Flask REST API. Flask services implement authorization and business workflows through SQLAlchemy, while MySQL views, functions, triggers, and a stored procedure demonstrate database-side capabilities. External map and model services are optional adapters with deterministic fallbacks.

**Primary stack:** Python 3, Flask, SQLAlchemy 2, Pydantic 2, PyMySQL, pytest, MySQL 8, Vue 3, Vite, TypeScript, Pinia, Vue Router, Element Plus, Axios, Vitest, Playwright.

## Working rules

- Implement one task at a time and keep each task independently testable.
- Add or update tests before completing each behavior.
- Never commit secrets, uploaded demo files, build output, or brainstorming artifacts.
- Keep the core workflow runnable without a map key or model API key.
- Prefer small service and component files over large multi-purpose modules.
- Run focused tests after each task and the full suite at each phase boundary.

## Phase 1 — Database foundation

### Task 1: Repository and environment skeleton

**Files**

- Create: `README.md`
- Create: `.env.example`
- Create: `backend/requirements.txt`
- Create: `backend/requirements-dev.txt`
- Create: `backend/uploads/.gitkeep`
- Create: `database/README.md`

**Work**

1. Document required Python, Node, npm, and MySQL versions.
2. Define environment variables for database URL, JWT secret, upload directory, map key, and optional model endpoint.
3. Add reproducible install and startup commands without real credentials.
4. Verify ignored runtime paths with `git status --short`.

**Verification**

- `python --version`
- `node --version`
- `npm --version`
- `mysql --version`

**Commit:** `chore: scaffold PawFinder project`

### Task 2: Core schema

**Files**

- Create: `database/schema.sql`
- Create: `database/tests/01_schema_constraints.sql`

**Work**

1. Write a failing SQL verification script that expects all 11 tables and required constraints.
2. Implement tables in dependency order: users, pets, pet photos, lost cases, sightings, sighting photos, matches, search areas, search tasks, reunion records, notifications.
3. Add primary keys, foreign keys, unique constraints, checks, defaults, timestamps, and delete policies.
4. Add indexes for public lists, matching rankings, task lookup, and notifications.
5. Make schema execution idempotent at database-reset level by dropping and recreating the application database only in a separate documented reset command, not in `schema.sql`.

**Verification**

- Execute `database/schema.sql` on an empty MySQL database.
- Execute `database/tests/01_schema_constraints.sql`.
- Confirm invalid role, invalid coordinate, duplicate match, and duplicate reunion inserts fail.

**Commit:** `feat(database): add normalized core schema`

### Task 3: Database objects and transactions

**Files**

- Create: `database/objects.sql`
- Create: `database/tests/02_database_objects.sql`
- Create: `database/tests/03_reunion_transaction.sql`

**Work**

1. Test and implement `fn_distance_km`.
2. Test and implement the three reporting views.
3. Test and implement high-score notification, first-cover, and closed-time triggers.
4. Test and implement `sp_confirm_reunion` with row locking, transaction handling, task closure, and notification creation.
5. Verify procedure rollback when the case is already reunited or the input is invalid.

**Verification**

- Run all database test scripts in filename order.
- Use `SHOW CREATE` for each view, function, trigger, and procedure.

**Commit:** `feat(database): add views triggers and reunion procedure`

### Task 4: Seed data and report queries

**Files**

- Create: `database/seed.sql`
- Create: `database/queries.sql`
- Create: `database/tests/04_seed_expectations.sql`

**Work**

1. Add deterministic users, password hashes, pets, cases, sightings, matches, tasks, reunion data, and notifications.
2. Include high, medium, low, confirmed, rejected, available, in-progress, completed, and reunited examples.
3. Add representative joins, grouping, subqueries, ranking, and statistics queries.
4. Add `EXPLAIN` statements for indexed queries.

**Verification**

- Reset database, then run schema, objects, seed, and all tests from scratch.
- Verify documented row counts and demonstration account credentials.

**Commit:** `test(database): add seed data and verification queries`

## Phase 2 — Flask API

### Task 5: Application factory and test harness

**Files**

- Create: `backend/run.py`
- Create: `backend/app/__init__.py`
- Create: `backend/app/create_app.py`
- Create: `backend/app/config.py`
- Create: `backend/app/extensions.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/errors.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_health.py`

**Work**

1. Write a failing health-check test.
2. Implement the Flask application factory, configuration classes, SQLAlchemy, migrations strategy, CORS, JWT, and standardized JSON errors.
3. Add request IDs and safe logging.
4. Add test configuration using an isolated MySQL test database.

**Verification**

- `pytest backend/tests/test_health.py -q`
- Start the development server and request `/api/v1/health`.

**Commit:** `feat(api): create Flask application foundation`

### Task 6: Authentication and user permissions

**Files**

- Create: `backend/app/models/user.py`
- Create: `backend/app/api/auth.py`
- Create: `backend/app/api/users.py`
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/services/auth_service.py`
- Create: `backend/app/security.py`
- Create: `backend/tests/test_auth.py`
- Create: `backend/tests/test_user_permissions.py`

**Work**

1. Test registration, login, disabled accounts, duplicate identities, token-protected access, password change, and admin-only actions.
2. Implement password hashing and JWT identity handling.
3. Implement reusable resource ownership and role guards.

**Verification**

- `pytest backend/tests/test_auth.py backend/tests/test_user_permissions.py -q`

**Commit:** `feat(api): add authentication and authorization`

### Task 7: Pets and uploads

**Files**

- Create: `backend/app/models/pet.py`
- Create: `backend/app/models/pet_photo.py`
- Create: `backend/app/api/pets.py`
- Create: `backend/app/schemas/pet.py`
- Create: `backend/app/services/upload_service.py`
- Create: `backend/tests/test_pets.py`
- Create: `backend/tests/test_uploads.py`

**Work**

1. Test owner-only CRUD, status-based deletion restrictions, image validation, cover uniqueness, and path safety.
2. Implement pet endpoints, safe random filenames, upload limits, cover selection, and file cleanup.

**Verification**

- `pytest backend/tests/test_pets.py backend/tests/test_uploads.py -q`

**Commit:** `feat(api): add pet profiles and photo uploads`

### Task 8: Lost cases and independent sightings

**Files**

- Create: `backend/app/models/lost_case.py`
- Create: `backend/app/models/sighting.py`
- Create: `backend/app/models/sighting_photo.py`
- Create: `backend/app/api/cases.py`
- Create: `backend/app/api/sightings.py`
- Create: `backend/app/schemas/case.py`
- Create: `backend/app/schemas/sighting.py`
- Create: `backend/tests/test_cases.py`
- Create: `backend/tests/test_sightings.py`

**Work**

1. Test public filtering, pagination, ownership, valid state transitions, coordinate boundaries, time validation, independent sightings, and admin hiding.
2. Implement CRUD and detail endpoints with public-field filtering.
3. Trigger matching-service jobs synchronously after creation so the course demo remains deterministic.

**Verification**

- `pytest backend/tests/test_cases.py backend/tests/test_sightings.py -q`

**Commit:** `feat(api): add lost cases and sightings`

### Task 9: Matching engine

**Files**

- Create: `backend/app/models/match.py`
- Create: `backend/app/services/matching.py`
- Create: `backend/app/api/matches.py`
- Create: `backend/tests/test_matching_scores.py`
- Create: `backend/tests/test_matching_workflow.py`

**Work**

1. Write table-driven tests for appearance, time, distance, thresholds, algorithm version, candidate filtering, idempotent recalculation, and owner review.
2. Implement deterministic `rule-v1` scoring.
3. Persist each component, total, distance, reason, version, and review state.
4. Call the database distance function or a mathematically identical Python implementation verified against it.

**Verification**

- `pytest backend/tests/test_matching_scores.py backend/tests/test_matching_workflow.py -q`

**Commit:** `feat(api): implement explainable clue matching`

### Task 10: Search collaboration and reunion transaction

**Files**

- Create: `backend/app/models/search.py`
- Create: `backend/app/models/reunion.py`
- Create: `backend/app/api/search.py`
- Create: `backend/app/api/reunions.py`
- Create: `backend/app/services/search_service.py`
- Create: `backend/app/services/reunion_service.py`
- Create: `backend/tests/test_search_tasks.py`
- Create: `backend/tests/test_reunions.py`

**Work**

1. Test area ownership, single active claimant, release, progress, completion, duplicate reunion, authorization, stored-procedure success, and rollback.
2. Implement transactional claim with conditional update and conflict response.
3. Call `sp_confirm_reunion` from the service and return its final state.

**Verification**

- `pytest backend/tests/test_search_tasks.py backend/tests/test_reunions.py -q`

**Commit:** `feat(api): add collaborative search and reunion workflow`

### Task 11: Notifications, AI fallback, and administration

**Files**

- Create: `backend/app/models/notification.py`
- Create: `backend/app/api/notifications.py`
- Create: `backend/app/api/ai_assist.py`
- Create: `backend/app/api/admin.py`
- Create: `backend/app/services/ai_service.py`
- Create: `backend/tests/test_notifications.py`
- Create: `backend/tests/test_ai_fallback.py`
- Create: `backend/tests/test_admin.py`

**Work**

1. Test unread counts, ownership, mark-as-read, trigger-created notifications, local description optimization, local summaries, remote timeouts, and admin statistics.
2. Implement deterministic local templates first.
3. Add an optional OpenAI-compatible HTTP adapter with strict timeout and response validation.

**Verification**

- `pytest backend/tests/test_notifications.py backend/tests/test_ai_fallback.py backend/tests/test_admin.py -q`
- `pytest backend/tests -q`

**Commit:** `feat(api): add notifications AI fallback and admin tools`

## Phase 3 — Vue interface

### Task 12: Frontend foundation and design system

**Files**

- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/styles/tokens.css`
- Create: `frontend/src/styles/global.css`
- Create: `frontend/src/router/index.ts`
- Create: `frontend/src/stores/auth.ts`
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/layouts/PublicLayout.vue`
- Create: `frontend/src/layouts/AppLayout.vue`

**Work**

1. Create the Vue TypeScript project and test setup.
2. Implement cream, coral, and sage design tokens from the approved A2 direction.
3. Implement responsive navigation, footer, route guards, API interceptor, loading state, and error surface.

**Verification**

- `npm test`
- `npm run build`

**Commit:** `feat(web): create Vue foundation and visual system`

### Task 13: Home, authentication, and public discovery

**Files**

- Create: `frontend/src/views/HomeView.vue`
- Create: `frontend/src/views/LoginView.vue`
- Create: `frontend/src/views/RegisterView.vue`
- Create: `frontend/src/views/CasesView.vue`
- Create: `frontend/src/components/cases/CaseCard.vue`
- Create: `frontend/src/components/common/EmptyState.vue`
- Create: `frontend/src/components/common/AppPagination.vue`
- Create: `frontend/src/tests/home.spec.ts`
- Create: `frontend/src/tests/auth.spec.ts`

**Work**

1. Test the primary actions, list loading, filters, pagination, empty states, login, registration, and auth persistence.
2. Implement the approved action-first warm-public-interest homepage.

**Verification**

- `npm test -- home.spec.ts auth.spec.ts`
- Visual check at desktop and mobile widths.

**Commit:** `feat(web): add homepage auth and case discovery`

### Task 14: Pet, case, and sighting forms

**Files**

- Create: `frontend/src/views/PetsView.vue`
- Create: `frontend/src/views/PetEditView.vue`
- Create: `frontend/src/views/CaseCreateView.vue`
- Create: `frontend/src/views/SightingCreateView.vue`
- Create: `frontend/src/components/forms/LocationFields.vue`
- Create: `frontend/src/components/uploads/PhotoUploader.vue`
- Create: `frontend/src/tests/forms.spec.ts`

**Work**

1. Test validation, image preview/removal, ownership errors, coordinate entry, AI optimization fallback, and successful submissions.
2. Implement focused multi-section forms without unnecessary wizard state.

**Verification**

- `npm test -- forms.spec.ts`
- Manual keyboard and validation check.

**Commit:** `feat(web): add pet case and sighting workflows`

### Task 15: Case detail, matching, map, and tasks

**Files**

- Create: `frontend/src/views/CaseDetailView.vue`
- Create: `frontend/src/views/MatchesView.vue`
- Create: `frontend/src/views/SearchMapView.vue`
- Create: `frontend/src/components/matches/MatchScore.vue`
- Create: `frontend/src/components/maps/CaseMap.vue`
- Create: `frontend/src/components/timeline/SightingTimeline.vue`
- Create: `frontend/src/components/search/SearchTaskPanel.vue`
- Create: `frontend/src/tests/case-detail.spec.ts`
- Create: `frontend/src/tests/search-tasks.spec.ts`

**Work**

1. Test component scores, review actions, time filters, map fallback, area creation, claim conflicts, progress, completion, and reunion confirmation.
2. Implement map adapter so no-key mode renders a coordinate list with the same data.
3. Place pet summary and primary actions above matching, timeline, map, and tasks.

**Verification**

- `npm test -- case-detail.spec.ts search-tasks.spec.ts`
- Manual map-key and no-key checks.

**Commit:** `feat(web): add matching map and search collaboration`

### Task 16: Personal center, notifications, and admin

**Files**

- Create: `frontend/src/views/ProfileView.vue`
- Create: `frontend/src/views/NotificationsView.vue`
- Create: `frontend/src/views/AdminView.vue`
- Create: `frontend/src/components/notifications/NotificationList.vue`
- Create: `frontend/src/components/admin/StatsCards.vue`
- Create: `frontend/src/tests/profile-admin.spec.ts`

**Work**

1. Test personal records, notification state, admin-only routing, account status actions, content state actions, and statistics.
2. Keep the admin interface compact and presentation-focused.

**Verification**

- `npm test -- profile-admin.spec.ts`
- `npm test`
- `npm run build`

**Commit:** `feat(web): add profile notifications and admin dashboard`

## Phase 4 — Integration and delivery

### Task 17: End-to-end demo and quality pass

**Files**

- Create: `e2e/playwright.config.ts`
- Create: `e2e/tests/reunion-flow.spec.ts`
- Create: `scripts/setup.ps1`
- Create: `scripts/start-dev.ps1`
- Create: `docs/test-cases.md`

**Work**

1. Automate database setup and local startup with non-destructive scripts.
2. Automate the complete owner → witness → match → volunteer → reunion story.
3. Verify invalid input, permission failure, duplicate claim, duplicate reunion, map fallback, and model fallback.
4. Run dependency, lint, type, unit, integration, SQL, and end-to-end checks.

**Verification**

- Full database reset and verification.
- `pytest backend/tests -q`
- `npm test`
- `npm run build`
- Playwright reunion flow.

**Commit:** `test: add end-to-end reunion workflow`

### Task 18: Documentation and presentation package

**Files**

- Update: `README.md`
- Create: `docs/requirements.md`
- Update or create: `docs/er-diagram.drawio`
- Create: `docs/data-dictionary.md`
- Create: `docs/report-outline.md`
- Create: `docs/presentation-outline.md`
- Create: `docs/demo-script.md`
- Create: `docs/video-checklist.md`

**Work**

1. Synchronize terminology, statuses, table names, screenshots, and credentials across code and documentation.
2. Produce report-ready database design text, SQL examples, test evidence, index analysis, and innovation explanation.
3. Produce a concise defense narrative and failure-safe demo order.
4. Verify a clean machine can follow README from database creation to browser access.

**Verification**

- Search documentation for stale names, missing files, placeholders, and secret values.
- Perform one complete clean setup rehearsal.
- Run the final automated suite after documentation-only changes.

**Commit:** `docs: complete course delivery package`

## Final acceptance checklist

- [ ] Clean database setup succeeds in documented order.
- [ ] All 11 tables and database objects exist.
- [ ] Backend unit and integration tests pass.
- [ ] Frontend tests and production build pass.
- [ ] End-to-end reunion flow passes.
- [ ] No-key map and model fallbacks work.
- [ ] Demo users and credentials match README.
- [ ] E-R diagram matches the implemented schema.
- [ ] Report and presentation use implemented features only.
- [ ] Git status contains no secret, upload, cache, or build artifacts.
