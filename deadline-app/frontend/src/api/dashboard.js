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

export const getTabPreview = async (file, tabName, headerRow) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await client.post(
        `/import/tab-preview?tab_name=${encodeURIComponent(tabName)}&header_row=${headerRow}`,
        formData
    )
    return response.data
}

export const previewImport = async (file, tabConfigs) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('config', JSON.stringify(tabConfigs))
    const response = await client.post('/import/preview', formData)
    return response.data
}

export const confirmImport = async (file, tabConfigs) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('config', JSON.stringify(tabConfigs))
    const response = await client.post('/import/confirm', formData)
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