import './globals.css';
import Navbar from './components/Navbar';
import { Amplify } from 'aws-amplify';
import { fetchAuthSession } from 'aws-amplify/auth';

Amplify.configure(
  {
    Auth: {
      Cognito: {
        userPoolId: process.env.NEXT_PUBLIC_USER_POOL_ID!,
        userPoolClientId: process.env.NEXT_PUBLIC_USER_POOL_CLIENT_ID!,
      },
    },
    API: {
      GraphQL: {
        endpoint: process.env.NEXT_PUBLIC_GRAPHQL_ENDPOINT!,
        region: process.env.NEXT_PUBLIC_AWS_REGION!,
        defaultAuthMode: 'apiKey',
        apiKey: process.env.NEXT_PUBLIC_API_KEY!,
      },
    },
  },
  { Auth: { fetchAuthSession } }
);

export const metadata = {
  title: 'Futsal League Manager',
  description: 'Manage your futsal league with ease',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        {children}
      </body>
    </html>
  );
}