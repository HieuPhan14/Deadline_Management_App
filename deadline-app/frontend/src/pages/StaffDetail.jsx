import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getStaffTasks } from '../api/staff'
import TaskCard from '../components/TaskCard'

export default function StaffDetail() {
    const [tasks, setTasks] = useState([])
    const [loading, setloading] = useState(true)
    const { staffId } = useParams()
    const navigate = useNavigate()   
    
    useEffect(() => {
        const fetchTasks = async () => {
            try {
                const data = await getStaffTasks(staffId)
                setTasks(data)
            } catch {
                console.log("Can't get data")
            } finally {
                setloading(false)
            }
        }
        fetchTasks()
    }, [staffId])

    if (loading) return <div>Loading...</div>

    return (
        <div>
            <button onClick={() => navigate('/dashboard')}>
                Back
            </button>
            <h1>Staff Tasks</h1>
            {tasks.length === 0
                ? <p>No task assigned</p>
                : tasks.map(task => (
                    <TaskCard key={task.id} task={task} />
                ))

            }
        </div>
    )
}