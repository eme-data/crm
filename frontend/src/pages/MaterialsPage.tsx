import { useState, useEffect } from 'react'
import { Plus, Search, Edit2, Trash2, Package } from 'lucide-react'
import DashboardLayout from '../components/DashboardLayout'
import { materialsService, Material } from '../services/materialsService'

export default function MaterialsPage() {
    const [materials, setMaterials] = useState<Material[]>([])
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState('')
    const [showAddModal, setShowAddModal] = useState(false)

    useEffect(() => {
        loadMaterials()
    }, [])

    const loadMaterials = async () => {
        try {
            setLoading(true)
            const data = await materialsService.list({
                active_only: true,
                search: search || undefined
            })
            setMaterials(data)
        } catch (error) {
            console.error('Erreur chargement matériaux:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleSearch = () => {
        loadMaterials()
    }

    const handleDelete = async (id: string) => {
        if (!confirm('Êtes-vous sûr de vouloir supprimer ce matériau ?')) return

        try {
            await materialsService.delete(id)
            loadMaterials()
        } catch (error) {
            console.error('Erreur suppression:', error)
            alert('Erreur lors de la suppression')
        }
    }

    return (
        <DashboardLayout>
            <div className="p-8">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 mb-2">Matériaux</h1>
                        <p className="text-gray-600">Gérez votre catalogue de matériaux</p>
                    </div>
                    <button
                        onClick={() => setShowAddModal(true)}
                        className="btn-primary flex items-center"
                    >
                        <Plus className="w-5 h-5 mr-2" />
                        Nouveau matériau
                    </button>
                </div>

                {/* Search & Stats */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
                    <div className="flex items-center gap-4">
                        <div className="flex-1 relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                            <input
                                type="text"
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                                placeholder="Rechercher par code ou nom..."
                                className="w-full pl-11 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                            />
                        </div>
                        <button
                            onClick={handleSearch}
                            className="btn-primary"
                        >
                            Rechercher
                        </button>
                    </div>

                    <div className="mt-4 flex items-center text-sm text-gray-600">
                        <Package className="w-4 h-4 mr-2" />
                        <span className="font-medium">{materials.length}</span>
                        <span className="ml-1">matériau{materials.length > 1 ? 'x' : ''}</span>
                    </div>
                </div>

                {/* Materials Table */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                    {loading ? (
                        <div className="p-12 text-center">
                            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
                            <p className="mt-4 text-gray-600">Chargement...</p>
                        </div>
                    ) : materials.length === 0 ? (
                        <div className="p-12 text-center">
                            <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                            <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun matériau</h3>
                            <p className="text-gray-600 mb-4">
                                {search
                                    ? 'Aucun résultat pour cette recherche'
                                    : 'Commencez par ajouter votre premier matériau'
                                }
                            </p>
                            <button
                                onClick={() => setShowAddModal(true)}
                                className="btn-primary"
                            >
                                <Plus className="w-4 h-4 mr-2 inline" />
                                Ajouter un matériau
                            </button>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-gray-50 border-b border-gray-200">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Code
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Nom
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Unité
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Prix EUR
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Prix LEI
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Fournisseur
                                        </th>
                                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Actions
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {materials.map((material) => (
                                        <tr key={material.id} className="hover:bg-gray-50">
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className="font-mono text-sm font-medium text-gray-900">
                                                    {material.code}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="text-sm font-medium text-gray-900">
                                                    {material.name_fr}
                                                </div>
                                                {material.name_ro && (
                                                    <div className="text-sm text-gray-500">{material.name_ro}</div>
                                                )}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                {material.unit}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                {material.price_eur.toFixed(2)} €
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                                {material.price_lei ? `${material.price_lei.toFixed(2)} LEI` : '-'}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                                {material.supplier || '-'}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                                                <button
                                                    className="text-blue-600 hover:text-blue-800 mr-3"
                                                    title="Modifier"
                                                >
                                                    <Edit2 className="w-4 h-4" />
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(material.id)}
                                                    className="text-red-600 hover:text-red-800"
                                                    title="Supprimer"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>

                {/* Info */}
                {!loading && materials.length > 0 && (
                    <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                        <p className="text-sm text-blue-800">
                            💡 <strong>Astuce :</strong> Pour importer votre matrice Excel,
                            rendez-vous dans <strong>Import → Excel</strong> depuis le menu.
                        </p>
                    </div>
                )}
            </div>
        </DashboardLayout>
    )
}
