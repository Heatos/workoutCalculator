import React, { useState, useEffect } from "react"

function App() {
    const [data, setData] = useState([{}])

    useEffect(() => {
        fetch("/workouts")
            .then(res => res.json())
            .then(data => {
                setData(data);
                console.log(data);
            });
    }, []);

    return (
        <div>
            {(typeof data.members === 'undefined') ? (
                <p>Loading...</p>
            ) : (
                    data.members.map((workout, i) => (
                        <p key={i}>{workout.name}</p>
                    ))
            )}
        </div>
    )
}

export default App