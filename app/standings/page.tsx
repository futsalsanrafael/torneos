'use client';
import { useState, useEffect } from 'react';
import { generateClient } from 'aws-amplify/data';
import type { Schema } from '../../amplify/data/resource';

const client = generateClient<Schema>();

export default function Standings() {
  const [standings, setStandings] = useState<Schema['Standing']['type'][]>([]);

  useEffect(() => {
    async function fetchStandings() {
      try {
        const { data: standings } = await client.models.Standing.list();
        setStandings(standings);
      } catch (error) {
        console.error('Error fetching standings:', error);
      }
    }
    fetchStandings();
  }, []);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">League Standings</h1>
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-blue-600 text-white">
            <th className="p-2">Team</th>
            <th className="p-2">Played</th>
            <th className="p-2">Won</th>
            <th className="p-2">Drawn</th>
            <th className="p-2">Lost</th>
            <th className="p-2">Points</th>
          </tr>
        </thead>
        <tbody>
          {standings.map((team) => (
            <tr key={team.id} className="border-t">
              <td className="p-2">{team.name}</td>
              <td className="p-2">{team.played}</td>
              <td className="p-2">{team.won}</td>
              <td className="p-2">{team.drawn}</td>
              <td className="p-2">{team.lost}</td>
              <td className="p-2">{team.points}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}