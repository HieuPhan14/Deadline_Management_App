import { useState } from 'react'
import { AuthContext } from './useAuth'

export function AuthProvider({ children }) {
    // initialize from sessionStorage so refresh doesn't log out
    const [token, setToken] = useState(
        sessionStorage.getItem('token') || null
    )

    const login = (newToken) => {
        sessionStorage.setItem('token', newToken)
        setToken(newToken)
    }

    const logout = () => {
        sessionStorage.removeItem('token')
        setToken(null)
    }

    return (
        <AuthContext.Provider value={{ token, login, logout}}>
            {children}
        </AuthContext.Provider>
    )
}
