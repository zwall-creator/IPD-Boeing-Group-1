## Sign-in Supabase DB and Login Page Breakdown

## Run and test:
From the repository root, run:
```bash
python3 -m http.server 8000 --directory src/frontend
```
Open <http://localhost:8000>. Select "Need an account? Sign up", make an account, 
confirm its email once it's sent out, then sign in and sign out
Check Authentication → Users in Supabase to verify the account and
Table Editor → profiles to verify its profile row in database

## How it works:
- auth.js uses the project URL and publishable key to connect the browser to Supabase
- Sign-up and sign-in requests go to supabase authentication, which manages passwords and sessions
- On sign-up, a database trigger makes a profile with the user's ID and optional display name
- Row-level security limits profile reads and updates to the signed-in owner
- The page currently authenticates users and shows their email; it doesn't
  yet load/edit profile data (future potential update)

## Things to improve:
Design, password security, profile configuration, logo/name, 