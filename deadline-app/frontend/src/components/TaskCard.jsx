import clsx from 'clsx'

function getDeadlineText(task) {
    if (task.is_recurring) return 'Recurring'
    if (task.days_remaining === null) return 'No deadline'
    if (task.days_remaining < 0) return `${Math.abs(task.days_remaining)} days overdue`
    if (task.days_remaining === 0) return 'Due today'
    return `${task.days_remaining} days left`
}   

export default function TaskCard({ task }) {
    const borderColor = {
        overdue: 'border-red-600',
        red_urgent: 'border-red-500',
        red: 'border-red-400',
        yellow: 'border-yellow-500',
        green: 'border-green-400'
    }[task.urgency] || 'border-grey-200'

    return (
        <div className={clsx(
            'border',
            borderColor
        )}>
            <p>{task.content}</p>
            <div>
                <span>{getDeadlineText(task)}</span>

                {task.staff_names.length > 0 && (
                    <span>{task.staff_names.join(', ')}</span>
                )}
            </div>
        </div>
    )
}