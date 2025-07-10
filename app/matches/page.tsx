'use client';
import { useState, useEffect } from 'react';
import { Auth, fetchAuthSession } from 'aws-amplify/auth';
import { generateClient } from 'aws-amplify/data';
import { useRouter } from 'next/navigation';
import type { Schema } from '../../amplify/data/resource';

const client = generateClient<Schema>();

export default function Matches() {
  const [matches, setMatches] = useState<Schema['Match']['type'][]>([]);
  const [newMatch, setNewMatch] = useState({
    team1: '',
    team2: '',
    date: '',
    time: '',
    location: '',
  });
  const [isAdmin, setIsAdmin] = useState(false);
  const router = useRouter();

  useEffect(() => {
    async function fetchMatches() {
      try {
        const { data: matches } = await client.models.Match.list();
        setMatches(matches);
      } catch (error) {
        console.error('Error fetching matches:', error);
      }
    }
    async function checkAdmin() {
      try {
        const { tokens } = await fetchAuthSession();
        const groups = (tokens?.accessToken.payload['cognito:groups'] as string[]) || [];
        setIsAdmin(groups.includes('Admins'));
      } catch (error) {
        setIsAdmin(false);
        router.push('/signin');
      }
    }
    fetchMatches();
    checkAdmin();
  }, [router]);

  const handleAddMatch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isAdmin) return alert('Only admins can add matches.');
    try {
      const { data: match } = await client.models.Match.create(newMatch);
      if (match) setMatches([...matches, match]);
      setNewMatch({ team1: '', team2: '', date: '', time: '', location: '' });
    } catch (error) {
      console.error('Error adding match:', error);
      alert('Failed to add match. Please try again.');
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Matches</h1>
      {isAdmin && (
        <form onSubmit={handleAddMatch} className="mb-4 space-y-2">
          <input
            type="text"
            value={newMatch.team1}
            onChange={(e) => setNewMatch({ ...newMatch, team1: e.target.value })}
            placeholder="Team 1"
            className="border p-2 w-full"
            required
          />
          <input
            type="text"
            value={newMatch.team2}
            onChange={(e) => setNewMatch({ ...newMatch, team2: e.target.value })}
            placeholder="Team 2"
            className="border p-2 w-full"
            required
          />
          <input
            type="date"
            value={newMatch.date}
            onChange={(e) => setNewMatch({ ...newMatch, date: e.target.value })}
            className="border p-2 w-full"
            required
          />
          <input
            type="time"
            value={newMatch.time}
            onChange={(e) => setNewMatch({ ...newMatch, time: e.target.value })}
            className="border p-2 w-full"
            required
          />
          <input
            type="text"
            value={newMatch.location}
            onChange={(e) => setNewMatch({ ...newMatch, location: e.target.value })}
            placeholder="Location"
            className="border p-2 w-full"
            required
          />
          <button type="submit" className="bg-blue-600 text-white p-2 rounded">Add Match</button>
        </form>
      )}
      <ul className="space-y-4">
        {matches.map((match) => (
          <li key={match.id} className="p-4 bg-gray-100 rounded shadow">
            <p className="font-semibold">{match.team1} vs {match.team2}</p>
            <p>Date: {match.date}</p>
            <p>Time: {match.time}</p>
            <p>Location: {match.location}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}