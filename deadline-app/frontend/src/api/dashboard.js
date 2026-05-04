import client from './client'

export const getDashboard = async () => {
    const response = await client.get('/dashboard/')
    return response.data
}

export const getStaffList = async () => {
    const response = await client.get('/dashboard/staff')
    return response.data
}

