import clsx from 'clsx'
import { Trash2 } from 'lucide-react'

function getDeadlineText(task) {
    if (task.is_recurring) return 'Recurring'
    if (task.days_remaining === null) return 'No deadline'
    if (task.days_remaining < 0) return `${Math.abs(task.days_remaining)} days overdue`
    if (task.days_remaining === 0) return 'Due today'
    return `${task.days_remaining} days left`
}   

export default function TaskCard({ task, onCancel }) {
    const borderColor = {
        overdue: 'border-red-600',
        red_urgent: 'border-red-500',
        red: 'border-red-400',
        yellow: 'border-yellow-500',
        green: 'border-green-400'
    }[task.urgency] || 'border-grey-200'

    return (
        <div className={clsx(
            'bg-white rounded-xl p-4 border-l-4 shadow-sm space-y-1 mb-2',
            borderColor
        )}>
            <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-gray-800">{task.content}</p>
                <button
                    onClick={() => onCancel(task)}
                    className="flex items-center justify-between text-xs text-gray-400 hover:text-red-500 transition-colors"
                >
                    Delete <Trash2 size={14} />
                </button>
            </div>
            <div className="flex items-center justify-between text-xs text-gray-500">
                <span>{getDeadlineText(task)}</span>
                {task.staff_names.length > 0 && (
                    <span>{task.staff_names.join(', ')}</span>
                )}
            </div>
        </div>
    )
}