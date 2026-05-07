import client from './client'

export const loginRequest = async (email, password) => {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)

    const response = await client.post('/auth/login', formData)
    return response.data.access_token
}