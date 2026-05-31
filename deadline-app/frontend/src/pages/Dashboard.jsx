import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth'
import { getDashboard, getStaffList, cancelDirective, cancelDocument, createTask } from '../api/dashboard'

const refreshDashboard = async (setDashboard, setStaff) => {
    const [dashboardData, staffData] = await Promise.all([getDashboard(), getStaffList()])
    setDashboard(dashboardData)
    setStaff(staffData)
}
import TaskCard from '../components/TaskCard'
import StaffCard from '../components/StaffCard'
import StaffPicker from '../components/StaffPicker'

export default function Dashboard() {
    const [dashboard, setDashboard] = useState(null)
    const [staff, setStaff] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [creating, setCreating] = useState(false)
    const [newJob, setNewJob] = useState({ content: '', deadline: '', source: 'document', staff_names: [] })
    const [saving, setSaving] = useState(false)
    const { logout } = useAuth()
    const navigate = useNavigate()
    const handleCancel = async (task) => {
        if (task.source === 'document') await cancelDocument(task.id)
        else await cancelDirective(task.id)
        await refreshDashboard(setDashboard, setStaff)
    }

    const handleUpdate = async () => {
        await refreshDashboard(setDashboard, setStaff)
    }

    const handleCreate = async () => {
        setSaving(true)
        try {
            await createTask({
                content: newJob.content,
                deadline: newJob.deadline || null,
                source: newJob.source,
                staff_names: newJob.staff_names,
            })
            setCreating(false)
            setNewJob({ content: '', deadline: '', source: 'document', staff_names: [] })
            await refreshDashboard(setDashboard, setStaff)
        } finally {
            setSaving(false)
        }
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
        <>
        <div className="min-h-screen bg-gray-100">
            {/* Header */}
            <header className="bg-white shadow-sm px-6 py-4 flex items-center justify-between">
                <div>
                    <h1 className="text-xl font-bold text-gray-800">Deadline Dashboard</h1>
                    <p className="text-xs text-gray-400">{new Date().toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
                </div>
                <div className="flex gap-2">
                    <button
                        className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white text-sm font-medium rounded-lg transition-colors"
                        onClick={() => setCreating(true)}
                        >+ Add Job
                    </button>
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
                                <TaskCard key={task.id} task={task} onCancel={handleCancel} onUpdate={handleUpdate} allStaff={staff} />
                            ))}
                        </section>
                    )}
                    {dashboard.red_urgent.length > 0 && (
                        <section>
                            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Due today/tomorrow</h2>
                            {dashboard.red_urgent.map(task => (
                                <TaskCard key={task.id} task={task} onCancel={handleCancel} onUpdate={handleUpdate} allStaff={staff} />
                            ))}
                        </section>
                    )}
                    {dashboard.red.length > 0 && (
                        <section>
                            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Due in 3 days</h2>
                            {dashboard.red.map(task => (
                                <TaskCard key={task.id} task={task} onCancel={handleCancel} onUpdate={handleUpdate} allStaff={staff} />
                            ))}
                        </section>
                    )}
                    {dashboard.yellow.length > 0 && (
                        <section>
                            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Due this week</h2>
                            {dashboard.yellow.map(task => (
                                <TaskCard key={task.id} task={task} onCancel={handleCancel} onUpdate={handleUpdate} allStaff={staff} />
                            ))}
                        </section>
                    )}
                    {dashboard.green.length > 0 && (
                        <section>
                            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">On track</h2>
                            {dashboard.green.map(task => (
                                <TaskCard key={task.id} task={task} onCancel={handleCancel} onUpdate={handleUpdate} allStaff={staff} />
                            ))}
                        </section>
                    )}
                </div>

                {/* Right - staff list */}
                <div className="w-64 shrink-0">
                    <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">Staff</h2>
                    <div className="space-y-2">
                        {staff.filter(m => m.pending_count > 0 || m.overdue_count > 0).map(member => (
                            <StaffCard key={member.id} member={member} />
                        ))}
                    </div>
                </div>
            </div>
        </div>

        {creating && (

            <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" onClick={() => setCreating(false)}>
                <div className="bg-white rounded-2xl shadow-xl p-6 w-full max-w-lg space-y-4" onClick={e => e.stopPropagation()}>
                    <h2 className="text-base font-semibold text-gray-800">Add Job</h2>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                        <select
                            value={newJob.source}
                            onChange={e => setNewJob(prev => ({ ...prev, source: e.target.value }))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="document">Document</option>
                            <option value="directive">Directive</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
                        <textarea
                            rows={4}
                            value={newJob.content}
                            onChange={e => setNewJob(prev => ({ ...prev, content: e.target.value }))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                            placeholder="Describe the job..."
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Deadline</label>
                        <input
                            type="date"
                            value={newJob.deadline}
                            onChange={e => setNewJob(prev => ({ ...prev, deadline: e.target.value }))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Assign Staff</label>
                        <StaffPicker
                            selected={newJob.staff_names}
                            onChange={(names) => setNewJob(prev => ({ ...prev, staff_names: names }))}
                            allStaff={staff}
                        />
                    </div>

                    <div className="flex justify-end gap-2">
                        <button
                            onClick={() => setCreating(false)}
                            className="px-4 py-2 text-sm text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                        >Cancel</button>
                        <button
                            onClick={handleCreate}
                            disabled={saving || !newJob.content.trim()}
                            className="px-4 py-2 text-sm text-white bg-green-600 hover:bg-green-700 disabled:bg-green-400 rounded-lg transition-colors"
                        >{saving ? 'Saving...' : 'Create'}</button>
                    </div>
                </div>
            </div>
        )}
        </>
    )
}
