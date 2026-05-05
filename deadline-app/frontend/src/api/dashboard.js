import client from './client'

export const getDashboard = async () => {
    const response = await client.get('/dashboard/')
    return response.data
}

export const getStaffList = async () => {
    const response = await client.get('/dashboard/staff')
    return response.data
}

export const detectTabs = async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await client.post('/import/detect-tabs', formData)
    return response.data
}

export const previewImport = async (file, tab1Name, tab2Name) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await client.post(
        `/import/preview?tab1_name=${encodeURIComponent(tab1Name)}&tab2_name=${encodeURIComponent(tab2Name)}`
        , formData
    )
    return response.data
}

export const confirmImport = async (file, tab1Name, tab2Name) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await client.post(
        `/import/confirm?tab1_name=${encodeURIComponent(tab1Name)}&tab2_name=${encodeURIComponent(tab2Name)}`
        , formData
    )
    return response.data
}
