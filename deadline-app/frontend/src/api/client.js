import axios from 'axios'

const API_URL = 'http://localhost:8000'

const client = axios.create({
    baseURL: API_URL
})

//attach token to every request automatically
client.interceptors.request.use((config) => {
    const token = sessionStorage.getItem('token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

export default client