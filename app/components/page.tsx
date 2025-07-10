'use client';
import { useState, useEffect } from 'react';
import { fetchAuthSession, signOut } from 'aws-amplify/auth';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function Navbar() {
  const [user, setUser] = useState<any>(null);
  const router = useRouter();

  useEffect(() => {
    async function checkUser() {
      try {
        const session = await fetchAuthSession();
        setUser(session.user);
      } catch (error) {
        setUser(null);
      }
    }
    checkUser();
  }, []);

  const handleSignOut = async () => {
    try {
      await signOut();
      setUser(null);
      router.push('/');
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  return (
    <nav className="bg-blue-600 text-white p-4">
      <div className="container mx-auto flex justify-between items-center">
        <Link href="/" className="text-2xl font-bold">Futsal League</Link>
        <div className="space-x-4">
          <Link href="/teams" className="hover:underline">Teams</Link>
          <Link href="/matches" className="hover:underline">Matches</Link>
          <Link href="/standings" className="hover:underline">Standings</Link>
          {user ? (
            <button onClick={handleSignOut} className="hover:underline">Sign Out</button>
          ) : (
            <>
              <Link href="/signin" className="hover:underline">Sign In</Link>
              <Link href="/signup" className="hover:underline">Sign Up</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}