import { useState } from 'react'

export default function StaffPicker({ selected, onChange, allStaff = [] }) {
    const [input, setInput] = useState('')

    const toggle = (name) => {
        onChange(selected.includes(name)
            ? selected.filter(n => n !== name)
            : [...selected, name]
        )
    }

    const addCustom = () => {
        const name = input.trim()
        if (name && !selected.includes(name)) {
            onChange([...selected, name])
        }
        setInput('')
    }

    const customNames = selected.filter(n => !allStaff.find(s => s.short_name === n))

    return (
        <div className="space-y-2">
            {allStaff.length > 0 && (
                <div className="grid grid-cols-2 gap-1 max-h-32 overflow-y-auto">
                    {allStaff.map(member => (
                        <label key={member.id} className="flex items-center gap-2 text-sm text-gray-700 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={selected.includes(member.short_name)}
                                onChange={() => toggle(member.short_name)}
                                className="accent-blue-600"
                            />
                            {member.short_name}
                        </label>
                    ))}
                </div>
            )}

            <div className="flex gap-2">
                <input
                    type="text"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && addCustom()}
                    placeholder="Type new staff name..."
                    className="flex-1 px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                    type="button"
                    onClick={addCustom}
                    className="px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors"
                >Add</button>
            </div>

            {customNames.length > 0 && (
                <div className="flex flex-wrap gap-1">
                    {customNames.map(name => (
                        <span key={name} className="flex items-center gap-1 px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded-full">
                            {name}
                            <button onClick={() => toggle(name)} className="hover:text-red-500">×</button>
                        </span>
                    ))}
                </div>
            )}
        </div>
    )
}
