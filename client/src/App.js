import { useEffect, useState } from "react";

export default function Workouts() {
  const [workouts, setWorkouts] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/workouts")
      .then(res => res.json())
      .then(data => setWorkouts(data))
      .catch(err => console.error("Error fetching workouts:", err));
  }, []);

  return (
    <div>
      <h2>Workouts</h2>
      <ul>
        {workouts.map(w => (
          <li key={w.id}>{w.name}</li>
        ))}
      </ul>
    </div>
  );
}
