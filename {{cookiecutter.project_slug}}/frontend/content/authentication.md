---
title: Authentication with Magic and Oauth2
description: "Background and approach to authentication in this stack."
navigation: false
---

# Authentication with Magic and Oauth2

## Minimum security requirements

The following is the baseline [recommended approach](https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Authentication_Cheat_Sheet.md) for ensuring safe app authentication:

- Any user account change must require current password verification to ensure that it's the legitimate user.
- Login page and all subsequent authenticated pages must be exclusively accessed over TLS or other strong transport.
- Account recovery must ensure that the starting point is a logged-out account.
- Where a state is unclear, use two tokens (one emailed, one stored in the browser) with a handshaking / fingerprinting protocol to ensure a chain of custody.
- An application should respond with a generic error message regardless of whether:
	- The user ID or password was incorrect.
	- The account does not exist.
	- The account is locked or disabled.
- Code should go through the same process, no matter what, allowing the application to return in approximately the same response time.
- In the words of [George Orwell](https://en.wikipedia.org/wiki/Politics_and_the_English_Language#Remedy_of_Six_Rules), "break any of these rules sooner than do anything outright barbarous".

[On passwords](https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Password_Storage_Cheat_Sheet.md):
- Use `Argon2id` with a minimum configuration of 15 MiB of memory, an iteration count of 2, and 1 degree of parallelism.
- Passwords shorter than 8 characters are considered to be weak (NIST SP800-63B).
- Maximum password length of 64 prevents long password Denial of Service attacks.
- Do not silently truncate passwords.
- Allow usage of all characters, including unicode and whitespace.

## Authenticated email-based _magic_ login

Most web applications permit account recovery through requesting a password reset via email. This is a weak point in the custodial chain _even_ assuming a savvy user adhering to best-practice password conventions. In which case, secure this and offer it as a login option ... a _magic_ login.

> Any custodial changes to user-controlled information must be treated as requiring full authentication. Do **not** assume that a logged-in user is the authorised account holder.

### Magic login workflow

- Ensure the user is logged out.
- User enters email in `frontend` and submits via API to `backend`.
- Check if an account exists, if not silently create one, and get the user `id`.
- Generate two 30-second-duration magic JWT tokens, each with a randomly-generated UUID `sub` (subject) and `fingerprint`, where `sub1 != sub2` and `fingerprint1 == fingerprint2`.
- One is emailed to the user (with `sub = user.id`) and the other is returned to the `frontend` to be stored in the user's browser.
- Once the user clicks on (or pastes) the magic / emailed link and returns to the browser, check that the `fingerprint` in the stored and submitted tokens are the same, and submit both to the `backend`.
- Validate the tokens, and check compliance with `sub` and `fingerprint` rules.
- If the custodial chain is secure, return an `access_token` and `refresh_token` to the `frontend`.
- Note that the tokens provide no meaningful information to an adversary. No email address or personal information.

### Oauth2 password login

Users may not always have access to email, or use a password manager, making it easier (and faster) to login with a password. A fallback to a stored password must be offered. You could also choose to enforce passwords for admin users.

### Account / password recovery and reset

Clearly a user does not _need_ a password to login with this process, and so there is no enforcement in the core stack. However, an application may require evidence of a deliberate decision in the custodial chain. Enforcing a password is part of that chain, and that raises the need to reset a password if it is ever lost.

Password recovery functions much the same as the magic workflow, with the same dual token validation process, except that the user now goes to a page that permits them to save a new password.

The user can also change their password while logged in, but - mindful of the rules for validation - they will need to provide their original password before doing so.

## Two-factor authentication

Time-based One-Time Password (TOTP) authentication extends the login process to include a _challenge-response_ component where the user needs to enter a time-based token _after_ their preferred login method.

This requires that the user:

- Install an authenticator app.
- Generate a QR code or key and pair that with their app.
- Confirm that they are paired.

After that, the user will be challenged to enter a 6-digit verification code to conclude each login.

The login workflow is extended as follows:

- TOTP requires the use of third-party token generators, and they seem to be stuck on `sha-1` hashing. That means deliberately dumbing down from `sha256`.
- After successful login (oauth2 or magic) instead of generating `access_token` and `refresh_token`, **instead** generate a special `access_token` with `totp = True` as a key in the token.
- Specifically test for this in each authentication check. `totp = True` can **only** be used to verify a TOTP submission, not for any other purpose. The user is not considered to be authenticated.
- When the user submits their verification code, `post` that, plus the `access_token` with `totp = True`, to complete authentication and receive the standard `access_token` and `refresh_token`.

As before, enabling or disabling TOTP requires full authentication with a password.

## Access and Refresh tokens

Persisting the authentication `state` of a user requires a mechanism to respond to an authentication challenge which does not inconvenience the user, while still maintaining security.

The standard method for doing so is via `access_token` and `refresh_token`, where:

- The access token is of short duration (30 minutes, or even less).
- The refresh token is of long duration (3 months, and sometimes indefinite).
- An access token can only be used to authenticate the user, and a refresh token can only be used to generate new access tokens.
- Access tokens are not stored, and refresh tokens are maintained in the database ... meaning they must be deliberately deactivated on use.
- When a user logs out, deactivate their refresh tokens.

Obviously, this still means that a long-living, active `refresh_token` is equivalent to authentication, which returns us to the caveat raised above:

> Any custodial changes to user-controlled information must be treated as requiring full authentication. Do **not** assume that a logged-in user is the authorised account holder.

## References

- [Python JOSE](https://python-jose.readthedocs.io/) to generate JWT tokens.
- [PassLib](https://passlib.readthedocs.io/) to manage hashing and TOTP.
- [OWASP authentication cheat sheet](https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Authentication_Cheat_Sheet.md)
- [OWASP password storage cheat sheet](https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Password_Storage_Cheat_Sheet.md)
- [Ensuring randomness](https://blog.cloudflare.com/ensuring-randomness-with-linuxs-random-number-generator/)