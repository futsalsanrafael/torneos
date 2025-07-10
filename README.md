# torneos
Partidos de La Asociación Futsal San Rafael

A Next.js app with AWS Amplify Gen 2 for managing a futsal league. Public pages for Home, Teams, and Standings; authenticated Matches page for admins.

## Structure

- `amplify/`: Backend definitions (auth, data).
- `app/`: Next.js App Router pages and components.
- `public/`: Static assets.
- `styles/`: Global CSS with Tailwind.

## Features

- **Home**: Matches of the day (public).
- **Teams**: Team list (public).
- **Standings**: League table (public).
- **Matches**: Match list, admin add match (authenticated).
- **Sign In/Sign Up**: Amplify Auth with Cognito.