import React, { useEffect, useState } from "react";

function App() {
  // -------------------------
  // State
  // -------------------------
  const [muscles, setMuscles] = useState([]);
  const [name, setName] = useState("");
  const [primaryMuscles, setPrimaryMuscles] = useState([]);
  const [secondaryMuscles, setSecondaryMuscles] = useState([]);
  const [status, setStatus] = useState("");

  // -------------------------
  // Load muscles from DB
  // -------------------------
  useEffect(() => {
    fetch("http://localhost:5000/workout.db")
      .then(res => res.json())
      .then(data => setMuscles(data))
      .catch(() => setStatus("Failed to load muscles"));
  }, []);

  // -------------------------
  // Handlers for menus
  // -------------------------
  const handlePrimaryChange = (e) => {
    const selected = Array.from(
      e.target.selectedOptions,
      option => Number(option.value)
    );
    setPrimaryMuscles(selected);
  };

  const handleSecondaryChange = (e) => {
    const selected = Array.from(
      e.target.selectedOptions,
      option => Number(option.value)
    );
    setSecondaryMuscles(selected);
  };

  // -------------------------
  // Submit
  // -------------------------
  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus("");

    const payload = {
      name,
      primary_muscles: primaryMuscles,
      secondary_muscles: secondaryMuscles,
    };

    try {
      const res = await fetch("http://localhost:5000/exercises", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error();

      setStatus("Exercise added!");
      setName("");
      setPrimaryMuscles([]);
      setSecondaryMuscles([]);
    } catch {
      setStatus("Error adding exercise");
    }
  };

  // -------------------------
  // UI
  // -------------------------
  return (
    <div style={{ padding: "2rem", maxWidth: "600px" }}>
      <h1>Add Exercise</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label>Exercise Name</label><br />
          <input
            type="text"
            value={name}
            required
            onChange={e => setName(e.target.value)}
          />
        </div>

        <h3>Primary Muscles</h3>
        <select
          multiple
          size={Math.min(6, muscles.length)}
          value={primaryMuscles.map(String)}
          onChange={handlePrimaryChange}
        >
          {muscles.map(m => (
            <option key={m.id} value={m.id}>
              {m.name}
            </option>
          ))}
        </select>

        <h3>Secondary Muscles</h3>
        <select
          multiple
          size={Math.min(6, muscles.length)}
          value={secondaryMuscles.map(String)}
          onChange={handleSecondaryChange}
        >
          {muscles.map(m => (
            <option key={m.id} value={m.id}>
              {m.name}
            </option>
          ))}
        </select>

        <br /><br />
        <button type="submit">Add Exercise</button>
      </form>

      {status && <p>{status}</p>}
    </div>
  );
}

export default App;
