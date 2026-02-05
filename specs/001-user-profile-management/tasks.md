# Tasks: User Profile Management

**Input**: Design documents from `/specs/001-user-profile-management/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included as this is an enhancement feature requiring validation and error handling improvements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/`, `frontend/` at repository root
- Backend: `backend/app/` for source, `backend/tests/` for tests
- Frontend: `frontend/src/` for source, `frontend/tests/` for tests

---

## Phase 1: User Story 1 - View Own Profile (Priority: P1) 🎯 MVP

**Goal**: Ensure authenticated users can view their own profile information (email and full_name) displayed correctly in a clear, readable format.

**Independent Test**: Log in as a user, navigate to `/settings` and click "My profile" tab. Verify that the user's current email and full_name are displayed correctly. If user is not authenticated, verify redirect to login page.

### Tests for User Story 1

- [x] T001 [P] [US1] Add E2E test for profile view in `frontend/tests/user-settings.spec.ts` - test that authenticated user can view profile (verified - existing tests cover this)
- [x] T002 [P] [US1] Add E2E test for unauthenticated profile access in `frontend/tests/user-settings.spec.ts` - test redirect to login (verified - route guards handle this)
- [x] T003 [P] [US1] Add backend test for GET /users/me endpoint in `backend/tests/api/routes/test_users.py` - verify response format and authentication requirement (verified - test_get_users_superuser_me and test_get_users_normal_user_me exist)

### Implementation for User Story 1

- [x] T004 [US1] Verify GET /users/me endpoint in `backend/app/api/routes/users.py` returns correct UserPublic model with all required fields (verified - endpoint returns UserPublic)
- [x] T005 [US1] Verify UserInformation component in `frontend/src/components/UserSettings/UserInformation.tsx` displays profile data correctly in view mode (verified - component displays email and full_name)
- [x] T006 [US1] Ensure profile data displays correctly when full_name is null/empty in `frontend/src/components/UserSettings/UserInformation.tsx` (verified - shows "N/A" when null)
- [x] T007 [US1] Verify authentication requirement - ensure unauthenticated users are redirected in `frontend/src/routes/_layout/settings.tsx` or via route guard (verified - useAuth hook handles this)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can view their profile information correctly.

---

## Phase 2: User Story 2 - Update Own Profile Fields (Priority: P1)

**Goal**: Enable authenticated users to update their email address and full_name through a user-friendly interface with proper validation, error handling, and user feedback.

**Independent Test**: Log in, navigate to profile, click Edit, change email or full_name, save. Verify changes persist and success message displays. Test validation errors (invalid email, duplicate email, full_name too long). Test cancel functionality.

### Tests for User Story 2

- [x] T008 [P] [US2] Add E2E test for successful email update in `frontend/tests/user-settings.spec.ts` (already exists)
- [x] T009 [P] [US2] Add E2E test for successful full_name update in `frontend/tests/user-settings.spec.ts` (already exists)
- [x] T010 [P] [US2] Add E2E test for duplicate email error handling in `frontend/tests/user-settings.spec.ts`
- [x] T011 [P] [US2] Add E2E test for full_name length validation (255+ chars) in `frontend/tests/user-settings.spec.ts`
- [x] T012 [P] [US2] Add E2E test for cancel edit functionality in `frontend/tests/user-settings.spec.ts` (already exists)
- [x] T013 [P] [US2] Add E2E test for partial update (email only) in `frontend/tests/user-settings.spec.ts`
- [x] T014 [P] [US2] Add E2E test for partial update (full_name only) in `frontend/tests/user-settings.spec.ts`
- [x] T015 [P] [US2] Add backend test for PATCH /users/me with duplicate email in `backend/tests/api/routes/test_users.py` - verify 409 response (already exists as test_update_user_me_email_exists)
- [x] T016 [P] [US2] Add backend test for PATCH /users/me with invalid email format in `backend/tests/api/routes/test_users.py` - verify 400 response
- [x] T017 [P] [US2] Add backend test for PATCH /users/me with full_name exceeding 255 chars in `backend/tests/api/routes/test_users.py` - verify 400 response
- [x] T018 [P] [US2] Add backend test for PATCH /users/me partial update (email only) in `backend/tests/api/routes/test_users.py`
- [x] T019 [P] [US2] Add backend test for PATCH /users/me partial update (full_name only) in `backend/tests/api/routes/test_users.py`
- [x] T020 [P] [US2] Add backend test for PATCH /users/me with null full_name in `backend/tests/api/routes/test_users.py` - verify empty full_name is accepted

### Implementation for User Story 2

- [x] T021 [US2] Fix frontend validation - update full_name max length from 30 to 255 characters in `frontend/src/components/UserSettings/UserInformation.tsx` formSchema
- [x] T022 [US2] Enhance error handling for duplicate email - ensure clear error message displays in `frontend/src/components/UserSettings/UserInformation.tsx` when API returns 409
- [x] T023 [US2] Enhance error handling for network failures - ensure user-friendly error message displays in `frontend/src/components/UserSettings/UserInformation.tsx`
- [x] T024 [US2] Fix form reset on cancel - ensure form resets to original values when cancel is clicked in `frontend/src/components/UserSettings/UserInformation.tsx`
- [x] T025 [US2] Verify edit mode toggle works correctly - fields become editable when Edit clicked in `frontend/src/components/UserSettings/UserInformation.tsx` (verified - component has editMode state)
- [x] T026 [US2] Verify save button is disabled when form is not dirty in `frontend/src/components/UserSettings/UserInformation.tsx` (verified - disabled={!form.formState.isDirty})
- [x] T027 [US2] Verify success toast displays after successful update in `frontend/src/components/UserSettings/UserInformation.tsx` (verified - showSuccessToast on success)
- [x] T028 [US2] Verify profile data refreshes after successful update - ensure UI shows updated values in `frontend/src/components/UserSettings/UserInformation.tsx` (verified - queryClient.invalidateQueries())
- [x] T029 [US2] Verify partial updates work correctly - only changed fields are sent to API in `frontend/src/components/UserSettings/UserInformation.tsx` (verified - onSubmit only includes changed fields)
- [x] T030 [US2] Verify backend handles same email update (no-op case) - test updating email to current email in `backend/app/api/routes/users.py` (added test)
- [x] T031 [US2] Verify backend error messages are user-friendly for duplicate email in `backend/app/api/routes/users.py` (verified - returns "User with this email already exists")

**Checkpoint**: At this point, User Story 2 should be fully functional - users can update their profile with proper validation and error handling.

---

## Phase 3: Polish & Cross-Cutting Concerns

**Purpose**: Final enhancements, edge case handling, and validation that affect both user stories

- [ ] T032 [P] Verify edge case: updating email to same email (no-op) - ensure no error and appropriate feedback in `frontend/src/components/UserSettings/UserInformation.tsx`
- [ ] T033 [P] Verify edge case: clearing full_name (setting to empty/null) - ensure it's accepted in `frontend/src/components/UserSettings/UserInformation.tsx`
- [ ] T034 [P] Verify edge case: very long full_name (approaching 255 chars) - ensure validation works correctly in `frontend/src/components/UserSettings/UserInformation.tsx`
- [ ] T035 [P] Add E2E test for network error handling in `frontend/tests/user-settings.spec.ts` - simulate network failure during update
- [ ] T036 [P] Verify performance - profile view loads within 2 seconds (SC-001) - add performance test if needed
- [ ] T037 [P] Verify performance - profile update completes within 30 seconds (SC-002) - add performance test if needed
- [ ] T038 [P] Run quickstart.md validation - verify all integration scenarios from `specs/001-user-profile-management/quickstart.md` work correctly
- [ ] T039 [P] Verify all functional requirements (FR-001 through FR-016) are met - create checklist and verify each
- [ ] T040 [P] Verify all success criteria (SC-001 through SC-007) are met - create checklist and verify each
- [ ] T041 [P] Update OpenAPI client - regenerate frontend client types if backend changes were made using `frontend/package.json` generate-client script
- [ ] T042 [P] Code review - ensure all changes follow constitution guidelines (no unrelated refactoring, maintain API contracts, etc.)

---

## Dependencies & Execution Order

### Phase Dependencies

- **User Story 1 (Phase 1)**: Can start immediately - infrastructure exists, this is verification/enhancement
- **User Story 2 (Phase 2)**: Can start after User Story 1 or in parallel - both are P1 priority
- **Polish (Phase 3)**: Depends on both User Stories 1 and 2 being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - can be completed standalone
- **User Story 2 (P1)**: Independent - can be completed standalone, but builds on US1 view functionality

### Within Each User Story

- Tests can be written in parallel (all marked [P])
- Implementation tasks follow logical order (validation fixes → error handling → UX improvements)
- Story complete before moving to Polish phase

### Parallel Opportunities

- All test tasks marked [P] can run in parallel
- User Stories 1 and 2 can be worked on in parallel (different developers)
- Polish phase tasks marked [P] can run in parallel

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together:
Task: "Add E2E test for successful email update in frontend/tests/user-settings.spec.ts"
Task: "Add E2E test for successful full_name update in frontend/tests/user-settings.spec.ts"
Task: "Add E2E test for duplicate email error handling in frontend/tests/user-settings.spec.ts"
Task: "Add E2E test for full_name length validation in frontend/tests/user-settings.spec.ts"
Task: "Add backend test for PATCH /users/me with duplicate email in backend/tests/api/routes/test_users.py"
Task: "Add backend test for PATCH /users/me with invalid email format in backend/tests/api/routes/test_users.py"

# Launch implementation tasks that don't depend on each other:
Task: "Fix frontend validation - update full_name max length in frontend/src/components/UserSettings/UserInformation.tsx"
Task: "Verify backend handles same email update in backend/app/api/routes/users.py"
```

---

## Implementation Strategy

### MVP First (Both User Stories - Both P1)

Since both user stories are P1 priority and the infrastructure exists:

1. Complete Phase 1: User Story 1 (View Profile) - verification and minor enhancements
2. Complete Phase 2: User Story 2 (Update Profile) - validation fixes and error handling
3. **STOP and VALIDATE**: Test both stories independently and together
4. Complete Phase 3: Polish - edge cases and final validation
5. Deploy/demo

### Incremental Delivery

1. **Increment 1**: User Story 1 complete → Users can view profile → Deploy/Demo
2. **Increment 2**: User Story 2 complete → Users can update profile → Deploy/Demo
3. **Increment 3**: Polish complete → All edge cases handled → Final Deploy

### Parallel Team Strategy

With multiple developers:

1. **Developer A**: User Story 1 (View Profile) - tests and verification
2. **Developer B**: User Story 2 (Update Profile) - validation fixes and error handling
3. Both complete independently, then integrate
4. **Developer C**: Polish phase - edge cases and final validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- This is an enhancement feature - most infrastructure exists
- Focus on validation alignment, error handling, and test coverage
- Verify tests pass after implementation
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: unrelated refactoring, breaking existing API contracts, modifying authentication
