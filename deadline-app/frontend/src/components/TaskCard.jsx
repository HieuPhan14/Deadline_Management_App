import { useState } from 'react'
import clsx from 'clsx'
import { Trash2 } from 'lucide-react'
import { updateDocument, updateDirective } from '../api/dashboard'
import StaffPicker from './StaffPicker'

function getDeadlineText(task) {
    if (task.is_recurring) return 'Recurring'
    if (task.days_remaining === null) return 'No deadline'
    if (task.days_remaining < 0) return `${Math.abs(task.days_remaining)} days overdue`
    if (task.days_remaining === 0) return 'Due today'
    return `${task.days_remaining} days left`
}

export default function TaskCard({ task, onCancel, onUpdate, allStaff = [] }) {
    const [editing, setEditing] = useState(false)
    const [content, setContent] = useState(task.content)
    const [deadline, setDeadline] = useState(task.deadline ?? '')
    const [selectedStaff, setSelectedStaff] = useState(task.staff_names)
    const [saving, setSaving] = useState(false)


    const borderColor = {
        overdue: 'border-red-600',
        red_urgent: 'border-red-500',
        red: 'border-red-400',
        yellow: 'border-yellow-500',
        green: 'border-green-400'
    }[task.urgency] || 'border-grey-200'

    const handleSave = async () => {
        setSaving(true)
        try {
            const data = {
                content: content || null,
                deadline: deadline || null,
                staff_names: selectedStaff,
            }
            if (task.source === 'document') {
                await updateDocument(task.id, data)
            } else {
                await updateDirective(task.id, data)
            }
            setEditing(false)
            onUpdate?.()
        } finally {
            setSaving(false)
        }
    }

    return (
        <>
            <div
                className={clsx(
                    'bg-white rounded-xl p-4 border-l-4 shadow-sm space-y-1 mb-2 cursor-pointer',
                    borderColor
                )}
                onClick={() => setEditing(true)}
            >
                <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-gray-800">{task.content}</p>
                    <button
                        onClick={(e) => { e.stopPropagation(); onCancel?.(task) }}
                        className="flex items-center gap-1 text-xs text-gray-400 hover:text-red-500 transition-colors"
                    >
                        Delete <Trash2 size={14} />
                    </button>
                </div>
                <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>
                        {getDeadlineText(task)}
                        {task.deadline && (
                            <span className="ml-2 text-gray-400">· {new Date(task.deadline).toLocaleDateString()}</span>
                        )}
                    </span>
                    {task.staff_names.length > 0 && (
                        <span>{task.staff_names.join(', ')}</span>
                    )}
                </div>
            </div>

            {editing && (
                <div
                    className="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
                    onClick={() => setEditing(false)}
                >
                    <div
                        className="bg-white rounded-2xl shadow-xl p-6 w-full max-w-lg space-y-4"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <h2 className="text-base font-semibold text-gray-800">Edit Task</h2>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
                            <textarea
                                rows={4}
                                value={content}
                                onChange={(e) => setContent(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Deadline</label>
                            <input
                                type="date"
                                value={deadline}
                                onChange={(e) => setDeadline(e.target.value)}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Staff</label>
                            <StaffPicker
                                selected={selectedStaff}
                                onChange={setSelectedStaff}
                                allStaff={allStaff}
                            />
                        </div>

                        <div className="flex justify-end gap-2">
                            <button
                                onClick={() => setEditing(false)}
                                className="px-4 py-2 text-sm text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleSave}
                                disabled={saving}
                                className="px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 rounded-lg transition-colors"
                            >
                                {saving ? 'Saving...' : 'Save'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    )
}
