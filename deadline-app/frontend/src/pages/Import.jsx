import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { detectTabs, previewImport, confirmImport } from '../api/dashboard'

export default function Import() {
    const [file, setFile] = useState(null)
    const [sheetNames, setSheetNames] = useState([])
    const [tab1, setTab1] = useState('')
    const [tab2, setTab2] = useState('')
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
            const data = await previewImport(file, tab1, tab2)
            setPreview(data)
            setStep(2)
        } finally {
            setLoading(false)
        }
    }

    const handleConfirm = async () => {
        setLoading(true)
        try {
            const data = await confirmImport(file, tab1, tab2)
            setResult(data)
            setStep(3)
        } catch (err) {
            alert(err.response?.data?.detail || 'Import failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div>
            <button onClick={() => navigate('/dashboard')}>Back</button>
            <h1>Import Excel</h1>

            {/* Step 1 -- upload and tab selection */}
            {step === 1 && (
                <div>
                    <input 
                        type="file"
                        accept=".xlsx"
                        onChange={handleFileChange}
                    />

                    {sheetNames.length > 0 && (
                        <div>
                            <div>
                                <label>Document tracking tab (Tab1)</label>
                                <select
                                    value={tab1}
                                    onChange={(e) => setTab1(e.target.value)}
                                >
                                    {sheetNames.map(name => (
                                        <option key={name} value={name}>{name}</option>
                                    ))}
                                </select>
                            </div>
                               
                            <div>
                                <label>Directives tab (Tab2)</label>
                                <select
                                    value={tab2}
                                    onChange={(e) => setTab2(e.target.value)}
                                >
                                    {sheetNames.map(name => (
                                        <option key={name} value={name}>{name}</option>
                                    ))}
                                </select>
                            </div>

                            <button
                                onClick={handlePreview}
                                disabled={loading}
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
                    <h2>Preview</h2>
                    <p>Documents: {preview.summary.documents_parsed}</p>
                    <p>Directives: {preview.summary.directives_parsed}</p>
                    <p>Staff found: {preview.summary.staff_found}</p>
                    <p>Flagged (no deadline): {preview.summary.total_flagged}</p>

                    {preview.flagged.length > 0 && (
                        <div>
                            <h3>Flagged rows - no deadline found</h3>
                            {preview.flagged.slice(0, 5).map((row, i) => (
                                <p key={i}>{row.content_summary || row.directive_content}</p>
                            ))}
                            {preview.flagged.length > 5 && (
                                <p>... and {preview.flagged.length - 5} more</p>
                            )}
                        </div>
                    )}

                    <div>
                        <button onClick={() => setStep(1)}>Back</button>
                        <button
                            onClick={handleConfirm}
                            disabled={loading}
                        >
                            {loading ? 'Importing...' : "Confirm Import"}
                        </button>
                    </div>

                </div>
            )}

            {/* Step 3 - Done */}
            {step === 3 && result && (
                <div>
                    <h2>Import Complete</h2>
                    <p>Documents imported: {result.documents_parsed}</p>
                    <p>Directives imported: {result.directives_parsed}</p>
                    <p>Staff found: {result.staff_found}</p>
                    <p>Flagged rows: {result.total_flagged}</p>
                    <button onClick={() => navigate('/dashboard')}>
                        Go to Dashboard
                    </button>
                </div>
            )}

        </div>
    )
}