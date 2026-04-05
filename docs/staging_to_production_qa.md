# RouteConnect Staging to Production QA

## 1) Security gate
- Confirm `JWT_SECRET` is production-grade and not default.
- Confirm `REQUIRE_AUTH_FOR_READS=true`.
- Confirm CORS is restricted to approved domains only.
- Confirm `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW_SECONDS` are set.
- Confirm Firebase service account is production account with least privilege.

## 2) Backend API gate
- Login with valid and invalid tokens:
  - valid Firebase ID token should pass.
  - invalid/expired token should return `401`.
- Verify role restrictions:
  - only admin/manager/dispatcher can `POST /api/notifications`.
- Verify rate limit:
  - burst requests over threshold should return `429`.

## 3) App gate
- Passenger login works with Firebase auth.
- Driver login works with admin-created credentials.
- Chat screen:
  - can load `/api/chat/messages`.
  - can send message via `/api/chat/messages`.
- Notifications screen:
  - can load `/api/notifications`.
  - can mark as read via `PATCH /api/notifications/{id}/read`.
- Crashlytics receives a non-fatal test event.

## 4) Web gate
- Admin can login.
- Admin can create driver accounts.
- Driver records list loads and delete action works.
- Live dashboard tabs load without console errors.

## 5) Operational gate
- Run CI workflow `Production Checks` and ensure all jobs pass.
- Verify backend logs are structured JSON in runtime logs.
- Verify mobile release build and web production build complete successfully.

## 6) Rollout gate
- Deploy backend to staging first.
- Smoke-test app/web against staging backend.
- Promote same artifact/config to production after sign-off.
