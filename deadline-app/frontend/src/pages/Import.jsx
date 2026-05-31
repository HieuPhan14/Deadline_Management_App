import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { detectTabs, previewImport, confirmImport } from '../api/dashboard'

export default function Import() {
    const [file, setFile] = useState(null)
    const [sheetNames, setSheetNames] = useState([])
    const [tab1, setTab1] = useState('')
    const [tab2, setTab2] = useState('')
    const [tab1HeaderRow, setTab1HeaderRow] = useState(6)
    const [tab2HeaderRow, setTab2HeaderRow] = useState(9)
    const [preview, setPreview] = useState(null)
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [step, setStep] = useState(1) // 1=upload, 2=preview, 3=done
    const navigate = useNavigate()

    const handleFileChange = async (e) => {
        const selectedFile = e.target.files[0]
        if (!selectedFile) return
        setFile(selectedFile)
        setLoading(true)
        try {
            const data = await detectTabs(selectedFile)
            setSheetNames(data.sheet_names)
            setTab1(data.suggested.tab1)
            setTab2(data.suggested.tab2)
        } finally {
            setLoading(false)
        }
    }

    const handlePreview = async () => {
        setLoading(true)
        try {
            const data = await previewImport(file, tab1, tab2, tab1HeaderRow, tab2HeaderRow)
            setPreview(data)
            setStep(2)
        } finally {
            setLoading(false)
        }
    }

    const handleConfirm = async () => {
        setLoading(true)
        try {
            const data = await confirmImport(file, tab1, tab2, tab1HeaderRow, tab2HeaderRow)
            setResult(data)
            setStep(3)
        } catch (err) {
            alert(err.response?.data?.detail || 'Import failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-gray-100 p-6">
            <div className="bg-white rounded-2xl shadow-lg p-8 max-w-2xl mx-auto">
                <button 
                    onClick={() => navigate('/dashboard')}
                    className="text-sm text-blue-600 hover:underline mb-4 block"
                    >Back to Dashboard
                </button>

                <h1 className="text-2xl font-bold text-gray-800 mb-6">Import Excel</h1>

                {/* Step 1 -- upload and tab selection */}
                {step === 1 && (
                    <div>
                        <input 
                            type="file"
                            accept=".xlsx"
                            onChange={handleFileChange}
                            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                        />

                        {sheetNames.length > 0 && (
                            <div>
                                <div className="mt-4 space-y-3">
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Document tracking tab (Tab1)</label>
                                    <select
                                        value={tab1}
                                        onChange={(e) => setTab1(e.target.value)}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    >
                                        {sheetNames.map(name => (
                                            <option key={name} value={name}>{name}</option>
                                        ))}
                                    </select>
                                </div>
                                
                                <div className="mt-4 space-y-3">
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Directives tab (Tab2)</label>
                                    <select
                                        value={tab2}
                                        onChange={(e) => setTab2(e.target.value)}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    >
                                        {sheetNames.map(name => (
                                            <option key={name} value={name}>{name}</option>
                                        ))}
                                    </select>
                                </div>

                                <div className="mt-4 flex gap-4">
                                    <div className="flex-1">
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Tab1 data starts at row</label>
                                        <input
                                            type="number"
                                            min={1}
                                            value={tab1HeaderRow}
                                            onChange={(e) => setTab1HeaderRow(Number(e.target.value))}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>
                                    <div className="flex-1">
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Tab2 data starts at row</label>
                                        <input
                                            type="number"
                                            min={1}
                                            value={tab2HeaderRow}
                                            onChange={(e) => setTab2HeaderRow(Number(e.target.value))}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>
                                </div>

                                <button
                                    onClick={handlePreview}
                                    disabled={loading}
                                    className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-sm font-medium rounded-lg transition-colors"
                                >
                                    {loading ? 'Loading...' : 'Preview Import'}
                                </button>
                            </div>
                        )}
                    </div>
                )}

                {/* Step 2 - Preview */}
                {step === 2 && preview && (
                    <div>
                        <h2 className="text-lg font-semibold text-gray-800 mb-3">Preview</h2>
                        <p className="text-sm text-gray-600">Documents: {preview.summary.documents_parsed}</p>
                        <p className="text-sm text-gray-600">Directives: {preview.summary.directives_parsed}</p>
                        <p className="text-sm text-gray-600">Staff found: {preview.summary.staff_found}</p>
                        <p className="text-sm text-gray-600">Flagged (no deadline): {preview.summary.total_flagged}</p>

                        {preview.flagged.length > 0 && (
                            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                                <h3 className="text-sm font-semibold text-yellow-700 mb-2">Flagged rows - no deadline found</h3>
                                {preview.flagged.slice(0, 5).map((row, i) => (
                                    <p key={i} className="text-sm text-yellow-800">{row.content_summary || row.directive_content}</p>
                                ))}
                                {preview.flagged.length > 5 && (
                                    <p className="text-sm text-yellow-600 mt-1">... and {preview.flagged.length - 5} more</p>
                                )}
                            </div>
                        )}

                        <div className="mt-6 flex gap-3">
                            <button 
                                onClick={() => setStep(1)}
                                className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 text-sm font-medium rounded-lg transition-colors"
                                >Back</button>
                            <button
                                onClick={handleConfirm}
                                disabled={loading}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-sm font-medium rounded-lg transition-colors"
                            >
                                {loading ? 'Importing...' : "Confirm Import"}
                            </button>
                        </div>

                    </div>
                )}

                {/* Step 3 - Done */}
                {step === 3 && result && (
                    <div>
                        <h2 className="text-lg font-semibold text-gray-800 mb-3">Import Complete</h2>
                        <p className="text-sm text-gray-600">Documents imported: {result.documents_parsed}</p>
                        <p className="text-sm text-gray-600">Directives imported: {result.directives_parsed}</p>
                        <p className="text-sm text-gray-600">Staff found: {result.staff_found}</p>
                        <p className="text-sm text-gray-600">Flagged rows: {result.total_flagged}</p>
                        <button 
                            onClick={() => navigate('/dashboard')}
                            className="mt-6 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
                            >
                            Go to Dashboard
                        </button>
                    </div>
                )}
            </div>
        </div>
    )
}