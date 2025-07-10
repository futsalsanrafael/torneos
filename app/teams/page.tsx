'use client';
import { useState, useEffect } from 'react';
import { generateClient } from 'aws-amplify/data';
import type { Schema } from '../../amplify/data/resource';

const client = generateClient<Schema>();

export default function Teams() {
  const [teams, setTeams] = useState<Schema['Team']['type'][]>([]);

  useEffect(() => {
    async function fetchTeams() {
      try {
        const { data: teams } = await client.models.Team.list();
        setTeams(teams);
      } catch (error) {
        console.error('Error fetching teams:', error);
      }
    }
    fetchTeams();
  }, []);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Teams</h1>
      <ul className="space-y-2">
        {teams.map((team) => (
          <li key={team.id} className="p-2 bg-gray-100 rounded">{team.name}</li>
        ))}
      </ul>
    </div>
  );
}