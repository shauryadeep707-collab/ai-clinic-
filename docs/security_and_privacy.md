# Security, Privacy & Compliance Guide

## Security Architecture
1. **Password Protection**: Passwords hashed using `bcrypt` with unique cryptographic salts.
2. **Session Integrity**: Stateless JSON Web Tokens (JWT) signed using HMAC-SHA256 with configurable expiry.
3. **Role-Based Access Control (RBAC)**: Backend endpoints strictly enforce `require_role(["patient"])`, `require_role(["doctor"])`, or `require_role(["admin"])`.
4. **Data Isolation**: Patients cannot view or query records belonging to other patients. Changing IDs in API endpoints triggers HTTP 403 Forbidden.
5. **Private Storage**: Uploaded PDF reports and doctor certificates are stored in private server directories outside the public web server document root.
6. **SQL Injection Defense**: 100% of database operations use parameterized queries (`?` or `:1`).
7. **Audit Logging**: Sensitive access actions (doctor verification approvals, permission grants) are recorded in the `AUDIT_LOGS` table.
