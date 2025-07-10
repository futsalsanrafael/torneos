'use client';
import { useState, useEffect } from 'react';
import { generateClient } from 'aws-amplify/data';
import type { Schema } from '../amplify/data/resource';

const client = generateClient<Schema>();

export default function Home() {
  const [matches, setMatches] = useState<Schema['Match']['type'][]>([]);
  const today = new Date().toISOString().split('T')[0];

  useEffect(() => {
    async function fetchMatches() {
      try {
        const { data: matches } = await client.models.Match.list({
          filter: { date: { eq: today } },
        });
        setMatches(matches);
      } catch (error) {
        console.error('Error fetching matches:', error);
      }
    }
    fetchMatches();
  }, []);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Matches of the Day</h1>
      {matches.length > 0 ? (
        <ul className="space-y-4">
          {matches.map((match) => (
            <li key={match.id} className="p-4 bg-gray-100 rounded shadow">
              <p className="font-semibold">{match.team1} vs {match.team2}</p>
              <p>Time: {match.time}</p>
              <p>Location: {match.location}</p>
            </li>
          ))}
        </ul>
      ) : (
        <p>No matches scheduled for today.</p>
      )}
    </div>
  );
}