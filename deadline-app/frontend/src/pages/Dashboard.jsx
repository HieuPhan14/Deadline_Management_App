import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth'
import { getDashboard, getStaffList, cancelDirective, cancelDocument } from '../api/dashboard'
import TaskCard from '../components/TaskCard'
import StaffCard from '../components/StaffCard'

export default function Dashboard() {
    const [dashboard, setDashboard] = useState(null)
    const [staff, setStaff] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const { logout } = useAuth()
    const navigate = useNavigate()
    const handleCancel = async (task) => {
        if (task.source === 'document') {
            await cancelDocument(task.id)
        } else {
            await cancelDirective(task.id)
        }
        const [dashboardData, staffData] = await Promise.all([getDashboard(), getStaffList()])
        setDashboard(dashboardData)
        setStaff(staffData)
    }

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [dashboardData, staffData] = await Promise.all([
                    getDashboard(),
                    getStaffList()
                ])
                setDashboard(dashboardData)
                setStaff(staffData)
            } catch {
                setError('Failed to load dashboard')
            } finally {
                setLoading(false)
            }
        }
        fetchData()
    }, [])

    if (loading) return <div className="min-h-screen flex items-center justify-center text-gray-500">Loading...</div>
    if (error) return <div className="min-h-screen flex items-center justify-center text-red-500">{error}</div>

    return (
        <div className="min-h-screen bg-gray-100">
            {/* Header */}
            <header className="bg-white shadow-sm px-6 py-4 flex items-center justify-between">
                <h1 className="text-xl font-bold text-gray-800">Deadline Dashboard</h1>
                <div className="flex gap-2">
                    <button 
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
                        onClick={() => navigate('/import')}
                        >Import Excel
                    </button>
                    <button 
                        onClick={logout}
                        className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 text-sm font-medium rounded-lg transition-colors"
                        >Logout
                    </button>
                </div>
            </header>

            {/* Summary */}
            <div className="px-6 py-4 grid grid-cols-3 gap-4">
                <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-center">
                    <p className="text-2xl font-bold text-red-600">{dashboard.summary.total_overdue}</p> 
                    <p className="text-sm text-red-500">Overdue</p>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 text-center">
                    <p className="text-2xl font-bold text-yellow-600">{dashboard.summary.total_yellow}</p>
                    <p className="text-sm text-yellow-500">Due Soon</p>
                </div>

                <div className="bg-green-50 border border-green-200 rounded-xl p-4 text-center">
                    <p className="text-2xl font-bold text-green-600">{dashboard.summary.total_green}</p>
                    <p className="text-sm text-green-500">On Track</p>
                </div>
            </div>

            <div className="px-6 pb-6 flex gap-6">
                {/* Left - task list */}
                <div className="flex-1 space-y-6">
                    {dashboard.overdue.length > 0 && (
                        <section>
                            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Overdue</h2>
                            {dashboard.overdue.map(task => (
                                <TaskCard key={task.id} task={task} onCancel={handleCancel}/>
                            ))}
                        </section>
                    )}
                    {dashboard.red_urgent.length > 0 && (
                        <section>
                            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Due today/tomorrow</h2>
                            {dashboard.red_urgent.map(task => (
                                <TaskCard key={task.id} task={task} onCancel={handleCancel}/>
                            ))}
                        </section>
                    )}
                    {dashboard.red.length > 0 && (
                        <section>
                            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Due in 3 days</h2>
                            {dashboard.red.map(task => (
                                <TaskCard key={task.id} task={task} onCancel={handleCancel}/>
                            ))}
                        </section>
                    )}
                    {dashboard.yellow.length > 0 && (
                        <section>
                            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Due this week</h2>
                            {dashboard.yellow.map(task => (
                                <TaskCard key={task.id} task={task} onCancel={handleCancel}/>
                            ))}
                        </section>
                    )}
                    {dashboard.green.length > 0 && (
                        <section>
                            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">On track</h2>
                            {dashboard.green.map(task => (
                                <TaskCard key={task.id} task={task} onCancel={handleCancel}/>
                            ))}
                        </section>
                    )}
                </div>

                {/* Right - staff list */}
                <div className="w-64 shrink-0">
                    <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Staff</h2>
                    <div className="space-y-2">
                        {staff.map(member => (
                            <StaffCard key={member.id} member={member} />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    )
}
