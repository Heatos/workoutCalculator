import React, { useState, useEffect } from "react"
import "./App.css"

function App() {
    const [workouts, setWorkouts] = useState([])
    const [exercises, setExercises] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [showForm, setShowForm] = useState(false)
    const [formData, setFormData] = useState({
        name: "",
        exerciseRows: [{ exercise: "", sets: "" }]
    })
    const [submitting, setSubmitting] = useState(false)

    useEffect(() => {
        fetchWorkouts()
        fetchExercises()
    }, [])

    const fetchWorkouts = () => {
        fetch("/workouts")
            .then(res => {
                if (!res.ok) {
                    throw new Error("Failed to fetch workouts")
                }
                return res.json()
            })
            .then(data => {
                setWorkouts(data.workouts || [])
                setLoading(false)
            })
            .catch(err => {
                setError(err.message)
                setLoading(false)
            })
    }

    const fetchExercises = () => {
        fetch("/exercises")
            .then(res => {
                if (!res.ok) {
                    throw new Error("Failed to fetch exercises")
                }
                return res.json()
            })
            .then(data => {
                setExercises(data.exercises || [])
            })
            .catch(err => {
                console.error("Error fetching exercises:", err)
            })
    }

    if (loading) {
        return (
            <div className="App">
                <h1>Workout Calculator</h1>
                <p>Loading workouts...</p>
            </div>
        )
    }

    if (error) {
        return (
            <div className="App">
                <h1>Workout Calculator</h1>
                <p className="error">Error: {error}</p>
            </div>
        )
    }

    const addExerciseRow = () => {
        setFormData({
            ...formData,
            exerciseRows: [...formData.exerciseRows, { exercise: "", sets: "" }]
        })
    }

    const removeExerciseRow = (index) => {
        const newRows = formData.exerciseRows.filter((_, i) => i !== index)
        setFormData({
            ...formData,
            exerciseRows: newRows
        })
    }

    const updateExerciseRow = (index, field, value) => {
        const newRows = [...formData.exerciseRows]
        newRows[index][field] = value
        setFormData({
            ...formData,
            exerciseRows: newRows
        })
    }

    const handleSubmit = async (e) => {
        e.preventDefault()
        setSubmitting(true)
        setError(null)

        const exercises = formData.exerciseRows.map(row => row.exercise).filter(ex => ex)
        const sets = formData.exerciseRows.map(row => parseInt(row.sets) || 0).filter((_, i) => exercises[i])

        if (!formData.name.trim()) {
            setError("Workout name is required")
            setSubmitting(false)
            return
        }

        if (exercises.length === 0) {
            setError("At least one exercise is required")
            setSubmitting(false)
            return
        }

        try {
            const response = await fetch("/workouts", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    name: formData.name,
                    exercises: exercises,
                    sets: sets
                })
            })

            const data = await response.json()

            if (!response.ok) {
                throw new Error(data.error || "Failed to add workout")
            }

            // Reset form and refresh workouts
            setFormData({
                name: "",
                exerciseRows: [{ exercise: "", sets: "" }]
            })
            setShowForm(false)
            fetchWorkouts()
            setSubmitting(false)
        } catch (err) {
            setError(err.message)
            setSubmitting(false)
        }
    }

    return (
        <div className="App">
            <h1>Workout Calculator</h1>
            
            <button 
                className="add-workout-btn" 
                onClick={() => setShowForm(!showForm)}
            >
                {showForm ? "Cancel" : "+ Add New Workout"}
            </button>

            {showForm && (
                <form className="workout-form" onSubmit={handleSubmit}>
                    <h2>Add New Workout</h2>
                    
                    <div className="form-group">
                        <label htmlFor="workout-name">Workout Name:</label>
                        <input
                            id="workout-name"
                            type="text"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            placeholder="e.g., Push Day"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Exercises:</label>
                        {formData.exerciseRows.map((row, index) => (
                            <div key={index} className="exercise-row">
                                <select
                                    value={row.exercise}
                                    onChange={(e) => updateExerciseRow(index, "exercise", e.target.value)}
                                    required
                                >
                                    <option value="">Select Exercise</option>
                                    {exercises.map(ex => (
                                        <option key={ex.id} value={ex.name}>
                                            {ex.name}
                                        </option>
                                    ))}
                                </select>
                                <input
                                    type="number"
                                    min="1"
                                    value={row.sets}
                                    onChange={(e) => updateExerciseRow(index, "sets", e.target.value)}
                                    placeholder="Sets"
                                    required
                                />
                                {formData.exerciseRows.length > 1 && (
                                    <button
                                        type="button"
                                        className="remove-btn"
                                        onClick={() => removeExerciseRow(index)}
                                    >
                                        Remove
                                    </button>
                                )}
                            </div>
                        ))}
                        <button
                            type="button"
                            className="add-row-btn"
                            onClick={addExerciseRow}
                        >
                            + Add Exercise
                        </button>
                    </div>

                    {error && <p className="error">{error}</p>}

                    <button 
                        type="submit" 
                        className="submit-btn"
                        disabled={submitting}
                    >
                        {submitting ? "Adding..." : "Add Workout"}
                    </button>
                </form>
            )}

            <h2>All Workouts</h2>
            {workouts.length === 0 ? (
                <p>No workouts found in the database.</p>
            ) : (
                <ul className="workout-list">
                    {workouts.map((workout) => (
                        <li key={workout.id} className="workout-item">
                            <span className="workout-id">#{workout.id}</span>
                            <span className="workout-name">{workout.name}</span>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    )
}

export default App