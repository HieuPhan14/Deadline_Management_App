import client from './client'

export const getStaffTasks = async (staffId) => {
    const response = await client.get(`/dashboard/staff/${staffId}`)
    return response.data
}