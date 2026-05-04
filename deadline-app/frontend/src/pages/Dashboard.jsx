import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth'
import { getDashboard, getStaffList } from '../api/dashboard'
import TaskCard from '../components/TaskCard'
import StaffCard from '../components/StaffCard'

export default function Dashboard() {
    const [dashboard, setDashboard] = useState(null)
    const [staff, setStaff] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    const { logout } = useAuth()
    const navigate = useNavigate()

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

    if (loading) return <div>Loading</div>
    if (error) return <div>{error}</div>

    return (
        <div>
            {/* Header */}
            <header>
                <h1>Deadline Dashboard</h1>
                <div>
                    <button onClick={() => navigate('/import')}>
                        Import Excel
                    </button>
                    <button onClick={logout}>
                        Logout
                    </button>
                </div>
            </header>

            {/* Summary */}
            <div>
                <div>{dashboard.summary.total_overdue} Overdue</div>
                <div>{dashboard.summary.total_yellow} Due soon</div>
                <div>{dashboard.summary.total_green} On track</div>
            </div>

            <div>
                {/* Left - task list */}
                <div>
                    {dashboard.overdue.length > 0 && (
                        <section>
                            <h2>Overdue</h2>
                            {dashboard.overdue.map(task => (
                                <TaskCard key={task.id} task={task} />
                            ))}
                        </section>
                    )}
                    {dashboard.red_urgent.length > 0 && (
                        <section>
                            <h2>Due today/tomorrow</h2>
                            {dashboard.red_urgent.map(task => (
                                <TaskCard key={task.id} task={task} />
                            ))}
                        </section>
                    )}
                    {dashboard.red.length > 0 && (
                        <section>
                            <h2>Due in 3 days</h2>
                            {dashboard.red.map(task => (
                                <TaskCard key={task.id} task={task} />
                            ))}
                        </section>
                    )}
                    {dashboard.yellow.length > 0 && (
                        <section>
                            <h2>Due this week</h2>
                            {dashboard.yellow.map(task => (
                                <TaskCard key={task.id} task={task} />
                            ))}
                        </section>
                    )}
                    {dashboard.green.length > 0 && (
                        <section>
                            <h2>On track</h2>
                            {dashboard.green.map(task => (
                                <TaskCard key={task.id} task={task} />
                            ))}
                        </section>
                    )}
                </div>

                {/* Right - staff list */}
                <div>
                    <h2>Staff</h2>
                    {staff.map(member => (
                        <StaffCard key={member.id} member={member} />
                    ))}
                </div>
            </div>
        </div>
    )
}
