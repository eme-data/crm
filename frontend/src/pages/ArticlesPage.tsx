import { useState, useEffect } from 'react'
import { Search, Trash2, RefreshCw, FileText } from 'lucide-react'
import DashboardLayout from '../components/DashboardLayout'
import { articlesService, Article } from '../services/articlesService'

export default function ArticlesPage() {
    const [articles, setArticles] = useState<Article[]>([])
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState('')

    useEffect(() => {
        loadArticles()
    }, [])

    const loadArticles = async () => {
        try {
            setLoading(true)
            const data = await articlesService.list({
                active_only: true,
                search: search || undefined
            })
            setArticles(data)
        } catch (error) {
            console.error('Erreur chargement articles:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleRecalculate = async (id: string) => {
        try {
            await articlesService.recalculate(id)
            loadArticles()
        } catch (error) {
            alert('Erreur lors du recalcul')
        }
    }

    const handleDelete = async (id: string) => {
        if (!confirm('Êtes-vous sûr de vouloir supprimer cet article ?')) return

        try {
            await articlesService.delete(id)
            loadArticles()
        } catch (error) {
            alert('Erreur lors de la suppression')
        }
    }

    return (
        <DashboardLayout>
            <div className="p-8">
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 mb-2">Articles</h1>
                        <p className="text-gray-600">Produits composés de matériaux et main d'œuvre</p>
                    </div>
                </div>

                {/* Search */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
                    <div className="flex items-center gap-4">
                        <div className="flex-1 relative">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                            <input
                                type="text"
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && loadArticles()}
                                placeholder="Rechercher par code ou nom..."
                                className="w-full pl-11 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                            />
                        </div>
                        <button onClick={loadArticles} className="btn-primary">
                            Rechercher
                        </button>
                    </div>

                    <div className="mt-4 flex items-center text-sm text-gray-600">
                        <FileText className="w-4 h-4 mr-2" />
                        <span className="font-medium">{articles.length}</span>
                        <span className="ml-1">article{articles.length > 1 ? 's' : ''}</span>
                    </div>
                </div>

                {/* Articles Table */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                    {loading ? (
                        <div className="p-12 text-center">
                            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
                            <p className="mt-4 text-gray-600">Chargement...</p>
                        </div>
                    ) : articles.length === 0 ? (
                        <div className="p-12 text-center">
                            <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                            <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun article</h3>
                            <p className="text-gray-600">
                                {search ? 'Aucun résultat pour cette recherche' : 'Les articles seront créés depuis l\'API'}
                            </p>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-gray-50 border-b border-gray-200">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nom</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Unité</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Coût Mat.</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Main d'œuvre</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Prix Total</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Marge</th>
                                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {articles.map((article) => (
                                        <tr key={article.id} className="hover:bg-gray-50">
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className="font-mono text-sm font-medium text-gray-900">{article.code}</span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="text-sm font-medium text-gray-900">{article.name}</div>
                                                {article.description && (
                                                    <div className="text-sm text-gray-500">{article.description}</div>
                                                )}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm">{article.unit}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                                {article.material_cost.toFixed(2)} €
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                                {article.labor_cost.toFixed(2)} €
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                {article.total_price.toFixed(2)} €
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                                {(article.margin * 100).toFixed(0)}%
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                                                <button
                                                    onClick={() => handleRecalculate(article.id)}
                                                    className="text-blue-600 hover:text-blue-800 mr-3"
                                                    title="Recalculer"
                                                >
                                                    <RefreshCw className="w-4 h-4" />
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(article.id)}
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
            </div>
        </DashboardLayout>
    )
}
