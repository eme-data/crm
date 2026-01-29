import { useState } from 'react'
import { Upload, FileSpreadsheet, CheckCircle, AlertCircle, Info } from 'lucide-react'
import DashboardLayout from '../components/DashboardLayout'
import { importService, ExcelStructure, ImportResponse } from '../services/importService'

export default function ImportPage() {
    const [file, setFile] = useState<File | null>(null)
    const [structure, setStructure] = useState<ExcelStructure | null>(null)
    const [selectedSheet, setSelectedSheet] = useState('')
    const [importType, setImportType] = useState<'materials' | 'services'>('materials')
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState<ImportResponse | null>(null)
    const [error, setError] = useState('')

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0]
        if (!selectedFile) return

        setFile(selectedFile)
        setStructure(null)
        setSelectedSheet('')
        setResult(null)
        setError('')

        // Détecter la structure
        try {
            setLoading(true)
            const data = await importService.detectStructure(selectedFile)
            setStructure(data)

            // Sélectionner automatiquement la première feuille
            const firstSheet = Object.keys(data.sheets)[0]
            if (firstSheet) setSelectedSheet(firstSheet)
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Erreur lors de la lecture du fichier')
        } finally {
            setLoading(false)
        }
    }

    const handleImport = async () => {
        if (!file || !selectedSheet) return

        try {
            setLoading(true)
            setError('')
            setResult(null)

            const data = importType === 'materials'
                ? await importService.importMaterials(file, selectedSheet)
                : await importService.importServices(file, selectedSheet)

            setResult(data)
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Erreur lors de l\'import')
        } finally {
            setLoading(false)
        }
    }

    return (
        <DashboardLayout>
            <div className="p-8 max-w-4xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Import Excel</h1>
                    <p className="text-gray-600">Importez votre matrice de prix depuis un fichier Excel</p>
                </div>

                {/* Type Selection */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
                    <h2 className="text-lg font-semibold text-gray-900 mb-4">Type d'import</h2>
                    <div className="flex gap-4">
                        <button
                            onClick={() => setImportType('materials')}
                            className={`flex-1 p-4 rounded-lg border-2 transition-all ${importType === 'materials'
                                    ? 'border-blue-500 bg-blue-50'
                                    : 'border-gray-200 hover:border-gray-300'
                                }`}
                        >
                            <FileSpreadsheet className={`w-6 h-6 mx-auto mb-2 ${importType === 'materials' ? 'text-blue-600' : 'text-gray-600'
                                }`} />
                            <span className={`block font-medium ${importType === 'materials' ? 'text-blue-900' : 'text-gray-900'
                                }`}>
                                Matériaux
                            </span>
                        </button>
                        <button
                            onClick={() => setImportType('services')}
                            className={`flex-1 p-4 rounded-lg border-2 transition-all ${importType === 'services'
                                    ? 'border-blue-500 bg-blue-50'
                                    : 'border-gray-200 hover:border-gray-300'
                                }`}
                        >
                            <FileSpreadsheet className={`w-6 h-6 mx-auto mb-2 ${importType === 'services' ? 'text-blue-600' : 'text-gray-600'
                                }`} />
                            <span className={`block font-medium ${importType === 'services' ? 'text-blue-900' : 'text-gray-900'
                                }`}>
                                Services
                            </span>
                        </button>
                    </div>
                </div>

                {/* File Upload */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
                    <h2 className="text-lg font-semibold text-gray-900 mb-4">1. Sélectionner le fichier</h2>

                    <label className="block">
                        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-400 transition-colors cursor-pointer">
                            <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                            <p className="text-gray-700 font-medium mb-2">
                                {file ? file.name : 'Cliquez pour sélectionner un fichier Excel'}
                            </p>
                            <p className="text-sm text-gray-500">
                                Formats acceptés : .xlsx, .xls
                            </p>
                            <input
                                type="file"
                                accept=".xlsx,.xls"
                                onChange={handleFileChange}
                                className="hidden"
                            />
                        </div>
                    </label>
                </div>

                {/* Structure Detection */}
                {structure && (
                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
                        <h2 className="text-lg font-semibold text-gray-900 mb-4">2. Sélectionner la feuille</h2>

                        <div className="space-y-3">
                            {Object.entries(structure.sheets).map(([sheetName, columns]) => (
                                <button
                                    key={sheetName}
                                    onClick={() => setSelectedSheet(sheetName)}
                                    className={`w-full text-left p-4 rounded-lg border-2 transition-all ${selectedSheet === sheetName
                                            ? 'border-blue-500 bg-blue-50'
                                            : 'border-gray-200 hover:border-gray-300'
                                        }`}
                                >
                                    <div className="flex items-center justify-between mb-2">
                                        <span className={`font-medium ${selectedSheet === sheetName ? 'text-blue-900' : 'text-gray-900'
                                            }`}>
                                            {sheetName}
                                        </span>
                                        {selectedSheet === sheetName && (
                                            <CheckCircle className="w-5 h-5 text-blue-600" />
                                        )}
                                    </div>
                                    <div className="text-xs text-gray-600">
                                        Colonnes : {columns.join(', ')}
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Import Button */}
                {structure && selectedSheet && (
                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
                        <h2 className="text-lg font-semibold text-gray-900 mb-4">3. Lancer l'import</h2>
                        <button
                            onClick={handleImport}
                            disabled={loading}
                            className="btn-primary w-full disabled:opacity-50"
                        >
                            {loading ? 'Import en cours...' : `Importer les ${importType === 'materials' ? 'matériaux' : 'services'}`}
                        </button>
                    </div>
                )}

                {/* Error */}
                {error && (
                    <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 flex items-start">
                        <AlertCircle className="w-5 h-5 text-red-600 mr-3 flex-shrink-0 mt-0.5" />
                        <div>
                            <p className="font-medium text-red-900">Erreur</p>
                            <p className="text-sm text-red-800">{error}</p>
                        </div>
                    </div>
                )}

                {/* Success Result */}
                {result && (
                    <div className="bg-green-50 border border-green-200 rounded-xl p-6">
                        <div className="flex items-start mb-4">
                            <CheckCircle className="w-6 h-6 text-green-600 mr-3 flex-shrink-0" />
                            <div>
                                <p className="font-semibold text-green-900 text-lg">{result.message}</p>
                                <p className="text-sm text-green-800 mt-1">
                                    Fichier : {result.file} | Feuille : {result.sheet}
                                </p>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div className="bg-white rounded-lg p-4">
                                <p className="text-sm text-gray-600">Créés</p>
                                <p className="text-2xl font-bold text-green-600">{result.statistics.created}</p>
                            </div>
                            <div className="bg-white rounded-lg p-4">
                                <p className="text-sm text-gray-600">Mis à jour</p>
                                <p className="text-2xl font-bold text-blue-600">{result.statistics.updated}</p>
                            </div>
                            <div className="bg-white rounded-lg p-4">
                                <p className="text-sm text-gray-600">Erreurs</p>
                                <p className="text-2xl font-bold text-red-600">{result.statistics.errors}</p>
                            </div>
                            <div className="bg-white rounded-lg p-4">
                                <p className="text-sm text-gray-600">Total</p>
                                <p className="text-2xl font-bold text-gray-900">{result.statistics.total}</p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Info */}
                <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mt-6">
                    <div className="flex items-start">
                        <Info className="w-5 h-5 text-blue-600 mr-3 flex-shrink-0 mt-0.5" />
                        <div className="text-sm text-blue-800">
                            <p className="font-semibold mb-2">Format attendu pour les {importType === 'materials' ? 'matériaux' : 'services'} :</p>
                            {importType === 'materials' ? (
                                <ul className="list-disc list-inside space-y-1">
                                    <li>Code (obligatoire)</li>
                                    <li>Nom FR (obligatoire)</li>
                                    <li>Nom RO (optionnel)</li>
                                    <li>Unité (obligatoire)</li>
                                    <li>Prix EUR (obligatoire)</li>
                                    <li>Prix LEI (optionnel, calculé automatiquement)</li>
                                    <li>Fournisseur (optionnel)</li>
                                </ul>
                            ) : (
                                <ul className="list-disc list-inside space-y-1">
                                    <li>Code (obligatoire)</li>
                                    <li>Nom (obligatoire)</li>
                                    <li>Unité (obligatoire)</li>
                                    <li>Prix Net (obligatoire)</li>
                                    <li>Prix Brut (obligatoire)</li>
                                    <li>Description (optionnel)</li>
                                </ul>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    )
}
