import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { detectTabs, getTabPreview, previewImport, confirmImport } from '../api/dashboard'

const emptyTab = () => ({
    tabName: '',
    headerRow: 1,
    taskType: 'document',
    columns: null,       // null = not loaded yet
    mapping: { contentCol: null, deadlineCol: null, staffCol: null },
})

export default function Import() {
    const [file, setFile]       = useState(null)
    const [sheetNames, setSheetNames] = useState([])
    const [tabs, setTabs]       = useState([emptyTab()])
    const [preview, setPreview] = useState(null)
    const [result, setResult]   = useState(null)
    const [loading, setLoading] = useState(false)
    const [step, setStep]       = useState(1)
    const navigate = useNavigate()

    // ── helpers ──────────────────────────────────────────────────────────────

    const updateTab = (idx, patch) =>
        setTabs(prev => prev.map((t, i) => i === idx ? { ...t, ...patch } : t))

    const updateMapping = (idx, patch) =>
        setTabs(prev => prev.map((t, i) =>
            i === idx ? { ...t, mapping: { ...t.mapping, ...patch } } : t
        ))

    const buildConfigs = () => tabs.map(t => ({
        tab_name:   t.tabName,
        header_row: t.headerRow,
        task_type:  t.taskType,
        mapping: {
            content_col:  t.mapping.contentCol,
            // document type: deadline lives in the same column as content
            deadline_col: t.taskType === 'document'
                ? t.mapping.contentCol
                : (t.mapping.deadlineCol ?? null),
            staff_col:    t.mapping.staffCol ?? null,
        }
    }))

    // ── handlers ─────────────────────────────────────────────────────────────

    const handleFileChange = async (e) => {
        const f = e.target.files[0]
        if (!f) return
        setFile(f)
        setLoading(true)
        try {
            const data = await detectTabs(f)
            setSheetNames(data.sheet_names)
            setTabs([{ ...emptyTab(), tabName: data.suggested.tab1 }])
        } finally {
            setLoading(false)
        }
    }

    const handleLoadColumns = async (idx) => {
        const tab = tabs[idx]
        if (!tab.tabName || !file) return
        setLoading(true)
        try {
            const data = await getTabPreview(file, tab.tabName, tab.headerRow)
            updateTab(idx, { columns: data.columns, mapping: { contentCol: null, deadlineCol: null, staffCol: null } })
        } finally {
            setLoading(false)
        }
    }

    const handlePreview = async () => {
        setLoading(true)
        try {
            const data = await previewImport(file, buildConfigs())
            setPreview(data)
            setStep(3)
        } finally {
            setLoading(false)
        }
    }

    const handleConfirm = async () => {
        setLoading(true)
        try {
            const data = await confirmImport(file, buildConfigs())
            setResult(data)
            setStep(4)
        } catch (err) {
            alert(err.response?.data?.detail || 'Import failed')
        } finally {
            setLoading(false)
        }
    }

    const canMap = tabs.every(t => t.mapping.contentCol !== null)

    // ── column dropdown ───────────────────────────────────────────────────────

    const ColSelect = ({ columns, value, onChange, required = false }) => (
        <select
            value={value ?? ''}
            onChange={e => onChange(e.target.value === '' ? null : Number(e.target.value))}
            className="w-full px-2 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
            {!required && <option value=''>— None —</option>}
            {required  && <option value=''>Select column</option>}
            {columns.map(col => (
                <option key={col.index} value={col.index}>
                    Col {col.index + 1} — {col.header}
                    {col.samples[0] ? ` (e.g. "${col.samples[0]}")` : ''}
                </option>
            ))}
        </select>
    )

    // ── render ────────────────────────────────────────────────────────────────

    return (
        <div className="min-h-screen bg-gray-100 p-6">
            <div className="bg-white rounded-2xl shadow-lg p-8 max-w-3xl mx-auto">
                <button onClick={() => navigate('/dashboard')} className="text-sm text-blue-600 hover:underline mb-4 block">
                    Back to Dashboard
                </button>
                <h1 className="text-2xl font-bold text-gray-800 mb-6">Import Excel</h1>

                {/* ── Step 1 — Upload ── */}
                {step === 1 && (
                    <div>
                        <input
                            type="file"
                            accept=".xlsx"
                            onChange={handleFileChange}
                            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                        />
                        {loading && <p className="mt-3 text-sm text-gray-400">Detecting sheets…</p>}
                        {sheetNames.length > 0 && (
                            <button
                                onClick={() => setStep(2)}
                                className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg"
                            >Configure Columns →</button>
                        )}
                    </div>
                )}

                {/* ── Step 2 — Column mapping ── */}
                {step === 2 && (
                    <div className="space-y-6">
                        {tabs.map((tab, idx) => (
                            <div key={idx} className="border border-gray-200 rounded-xl p-4 space-y-4">
                                <div className="flex items-center justify-between">
                                    <h2 className="text-sm font-semibold text-gray-700">Tab {idx + 1}</h2>
                                    {idx > 0 && (
                                        <button
                                            onClick={() => setTabs(prev => prev.filter((_, i) => i !== idx))}
                                            className="text-xs text-red-400 hover:text-red-600"
                                        >Remove</button>
                                    )}
                                </div>

                                {/* Sheet + header row + type */}
                                <div className="grid grid-cols-3 gap-3">
                                    <div>
                                        <label className="block text-xs font-medium text-gray-600 mb-1">Sheet</label>
                                        <select
                                            value={tab.tabName}
                                            onChange={e => updateTab(idx, { tabName: e.target.value, columns: null })}
                                            className="w-full px-2 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        >
                                            <option value=''>Select sheet</option>
                                            {sheetNames.map(n => <option key={n} value={n}>{n}</option>)}
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-xs font-medium text-gray-600 mb-1">Data starts at row</label>
                                        <input
                                            type="number" min={1}
                                            value={tab.headerRow}
                                            onChange={e => updateTab(idx, { headerRow: Number(e.target.value), columns: null })}
                                            className="w-full px-2 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-xs font-medium text-gray-600 mb-1">Type</label>
                                        <select
                                            value={tab.taskType}
                                            onChange={e => updateTab(idx, { taskType: e.target.value })}
                                            className="w-full px-2 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        >
                                            <option value="document">Content &amp; Deadline in same column</option>
                                            <option value="directive">Separate content &amp; deadline columns</option>
                                        </select>
                                    </div>
                                </div>

                                <button
                                    onClick={() => handleLoadColumns(idx)}
                                    disabled={!tab.tabName || loading}
                                    className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm rounded-lg disabled:opacity-50"
                                >
                                    {loading ? 'Loading…' : 'Load Columns'}
                                </button>

                                {/* Column preview table */}
                                {tab.columns && (
                                    <div className="space-y-3">
                                        <div className="overflow-x-auto rounded-lg border border-gray-100">
                                            <table className="text-xs w-full">
                                                <thead className="bg-gray-50">
                                                    <tr>
                                                        {tab.columns.map(col => (
                                                            <th key={col.index} className="px-2 py-1.5 text-left font-medium text-gray-600 border-r border-gray-100 last:border-r-0">
                                                                <span className="text-gray-400">Col {col.index + 1}</span><br />
                                                                {col.header}
                                                            </th>
                                                        ))}
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {[0, 1, 2].map(rowIdx => (
                                                        <tr key={rowIdx} className="border-t border-gray-100">
                                                            {tab.columns.map(col => (
                                                                <td key={col.index} className="px-2 py-1 text-gray-500 border-r border-gray-100 last:border-r-0 max-w-[120px] truncate">
                                                                    {col.samples[rowIdx] ?? ''}
                                                                </td>
                                                            ))}
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>

                                        {/* Field mapping */}
                                        <div className="grid grid-cols-3 gap-3">
                                            {tab.taskType === 'document' ? (
                                                <div>
                                                    <label className="block text-xs font-medium text-gray-600 mb-1">Content + Deadline column <span className="text-red-400">*</span></label>
                                                    <ColSelect
                                                        columns={tab.columns}
                                                        value={tab.mapping.contentCol}
                                                        onChange={v => updateMapping(idx, { contentCol: v })}
                                                        required
                                                    />
                                                </div>
                                            ) : (
                                                <>
                                                    <div>
                                                        <label className="block text-xs font-medium text-gray-600 mb-1">Content column <span className="text-red-400">*</span></label>
                                                        <ColSelect
                                                            columns={tab.columns}
                                                            value={tab.mapping.contentCol}
                                                            onChange={v => updateMapping(idx, { contentCol: v })}
                                                            required
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block text-xs font-medium text-gray-600 mb-1">Deadline column</label>
                                                        <ColSelect
                                                            columns={tab.columns}
                                                            value={tab.mapping.deadlineCol}
                                                            onChange={v => updateMapping(idx, { deadlineCol: v })}
                                                        />
                                                    </div>
                                                </>
                                            )}
                                            <div>
                                                <label className="block text-xs font-medium text-gray-600 mb-1">Staff column</label>
                                                <ColSelect
                                                    columns={tab.columns}
                                                    value={tab.mapping.staffCol}
                                                    onChange={v => updateMapping(idx, { staffCol: v })}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}

                        {/* Add second tab */}
                        {tabs.length < 2 && (
                            <button
                                onClick={() => setTabs(prev => [...prev, { ...emptyTab(), tabName: sheetNames[1] ?? '' }])}
                                className="text-sm text-blue-600 hover:underline"
                            >+ Add another tab</button>
                        )}

                        <div className="flex gap-3 pt-2">
                            <button onClick={() => setStep(1)} className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm rounded-lg">Back</button>
                            <button
                                onClick={handlePreview}
                                disabled={loading || !canMap}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-sm font-medium rounded-lg"
                            >{loading ? 'Loading…' : 'Preview Import'}</button>
                        </div>
                    </div>
                )}

                {/* ── Step 3 — Preview ── */}
                {step === 3 && preview && (
                    <div>
                        <h2 className="text-lg font-semibold text-gray-800 mb-3">Preview</h2>
                        <p className="text-sm text-gray-600">Documents: {preview.summary.documents_parsed}</p>
                        <p className="text-sm text-gray-600">Directives: {preview.summary.directives_parsed}</p>
                        <p className="text-sm text-gray-600">Staff found: {preview.summary.staff_found}</p>
                        <p className="text-sm text-gray-600">Flagged (no deadline): {preview.summary.total_flagged}</p>

                        {preview.flagged.length > 0 && (
                            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                                <h3 className="text-sm font-semibold text-yellow-700 mb-2">Flagged — no deadline found</h3>
                                {preview.flagged.slice(0, 5).map((row, i) => (
                                    <p key={i} className="text-sm text-yellow-800 truncate">{row.content}</p>
                                ))}
                                {preview.flagged.length > 5 && (
                                    <p className="text-sm text-yellow-600 mt-1">… and {preview.flagged.length - 5} more</p>
                                )}
                            </div>
                        )}

                        <div className="mt-6 flex gap-3">
                            <button onClick={() => setStep(2)} className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 text-sm rounded-lg">Back</button>
                            <button
                                onClick={handleConfirm}
                                disabled={loading}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-sm font-medium rounded-lg"
                            >{loading ? 'Importing…' : 'Confirm Import'}</button>
                        </div>
                    </div>
                )}

                {/* ── Step 4 — Done ── */}
                {step === 4 && result && (
                    <div>
                        <h2 className="text-lg font-semibold text-gray-800 mb-3">Import Complete</h2>
                        <p className="text-sm text-gray-600">Documents imported: {result.documents_parsed}</p>
                        <p className="text-sm text-gray-600">Directives imported: {result.directives_parsed}</p>
                        <p className="text-sm text-gray-600">Staff found: {result.staff_found}</p>
                        <p className="text-sm text-gray-600">Flagged rows: {result.total_flagged}</p>
                        <button
                            onClick={() => navigate('/dashboard')}
                            className="mt-6 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg"
                        >Go to Dashboard</button>
                    </div>
                )}
            </div>
        </div>
    )
}
