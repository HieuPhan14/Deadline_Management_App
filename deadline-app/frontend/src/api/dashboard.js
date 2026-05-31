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

export const previewImport = async (file, tab1Name, tab2Name, tab1HeaderRow, tab2HeaderRow) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await client.post(
        `/import/preview?tab1_name=${encodeURIComponent(tab1Name)}&tab2_name=${encodeURIComponent(tab2Name)}&tab1_header_row=${tab1HeaderRow}&tab2_header_row=${tab2HeaderRow}`,
        formData
    )
    return response.data
}

export const confirmImport = async (file, tab1Name, tab2Name, tab1HeaderRow, tab2HeaderRow) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await client.post(
        `/import/confirm?tab1_name=${encodeURIComponent(tab1Name)}&tab2_name=${encodeURIComponent(tab2Name)}&tab1_header_row=${tab1HeaderRow}&tab2_header_row=${tab2HeaderRow}`,
        formData
    )
    return response.data
}

export async function createTask(data) {
    return client.post('/tasks', data)
}

export async function updateDocument(docID, data) {
    return client.patch(`/tasks/documents/${docID}`, data)
}

export async function updateDirective(dirID, data) {
    return client.patch(`/tasks/directives/${dirID}`, data)
}

export async function cancelDocument(docID) {
    return client.patch(`/tasks/documents/${docID}/cancel`)
}

export async function cancelDirective(dirID) {
    return client.patch(`/tasks/directives/${dirID}/cancel`)
}