import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getStaffTasks } from '../api/staff'
import { getStaffList, cancelDocument, cancelDirective } from '../api/dashboard'
import TaskCard from '../components/TaskCard'

export default function StaffDetail() {
    const [tasks, setTasks] = useState([])
    const [allStaff, setAllStaff] = useState([])
    const [loading, setLoading] = useState(true)
    const { staffId } = useParams()
    const navigate = useNavigate()

    const fetchTasks = async () => {
        try {
            const data = await getStaffTasks(staffId)
            setTasks(data)
        } catch {
            console.log("Can't refresh tasks")
        }
    }

    useEffect(() => {
        const init = async () => {
            try {
                const [taskData, staffData] = await Promise.all([
                    getStaffTasks(staffId),
                    getStaffList()
                ])
                setTasks(taskData)
                setAllStaff(staffData)
            } catch {
                console.log("Can't get data")
            } finally {
                setLoading(false)
            }
        }
        init()
    }, [staffId])

    const handleCancel = async (task) => {
        if (task.source === 'document') await cancelDocument(task.id)
        else await cancelDirective(task.id)
        await fetchTasks()
    }

    const handleUpdate = async () => {
        await fetchTasks()
    }

    if (loading) return <div className="min-h-screen flex items-center justify-center text-gray-500">Loading...</div>

    return (
        <div className="min-h-screen bg-gray-100 p-6">
            <div className="bg-white rounded-2xl shadow-lg p-8 max-w-2xl mx-auto">
                <button
                    onClick={() => navigate('/dashboard')}
                    className="text-sm text-blue-600 hover:underline mb-4 block"
                >Back to Dashboard
                </button>
                <h1 className="text-2xl font-bold text-gray-800 mb-6">Staff Tasks</h1>
                {tasks.length === 0
                    ? <p className="text-sm text-gray-500">No task assigned</p>
                    : <div className="space-y-2">
                        {tasks.map(task => (
                            <TaskCard
                                key={task.id}
                                task={task}
                                onCancel={handleCancel}
                                onUpdate={handleUpdate}
                                allStaff={allStaff}
                            />
                        ))}
                    </div>
                }
            </div>
        </div>
    )
}
