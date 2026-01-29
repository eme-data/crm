import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import MaterialsPage from './pages/MaterialsPage'
import ArticlesPage from './pages/ArticlesPage'
import ServicesPage from './pages/ServicesPage'
import ImportPage from './pages/ImportPage'
import { authService } from './services/authService'

// Protected Route Component
function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const isAuthenticated = authService.isAuthenticated()

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />
    }

    return <>{children}</>
}

function App() {
    return (
        <BrowserRouter>
            <Routes>
                {/* Public Routes */}
                <Route path="/login" element={<LoginPage />} />

                {/* Protected Routes */}
                <Route
                    path="/dashboard"
                    element={
                        <ProtectedRoute>
                            <DashboardPage />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/materials"
                    element={
                        <ProtectedRoute>
                            <MaterialsPage />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/articles"
                    element={
                        <ProtectedRoute>
                            <ArticlesPage />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/services"
                    element={
                        <ProtectedRoute>
                            <ServicesPage />
                        </ProtectedRoute>
                    }
                />

                <Route
                    path="/import"
                    element={
                        <ProtectedRoute>
                            <ImportPage />
                        </ProtectedRoute>
                    }
                />

                {/* Default redirect */}
                <Route path="/" element={<Navigate to="/dashboard" replace />} />

                {/* 404 */}
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
        </BrowserRouter>
    )
}

export default App
