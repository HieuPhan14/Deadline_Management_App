import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/useAuth'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import StaffDetail from './pages/StaffDetail'
import Import from './pages/Import'

function PrivateRoute({ children }) {
    const { token } = useAuth()
    return token ? children : <Navigate to="/login" />
}

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/dashboard" element={
                    <PrivateRoute><Dashboard /></PrivateRoute>
                } />
                <Route path="/staff/:staffId" element={
                    <PrivateRoute><StaffDetail /></PrivateRoute>
                } />
                <Route path="/import" element={
                    <PrivateRoute><Import /></PrivateRoute>
                } />
                <Route path="/" element={<Navigate to="/dashboard" />} />
            </Routes>
        </BrowserRouter>
    )
}

export default App
