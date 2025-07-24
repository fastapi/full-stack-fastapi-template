"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { 
  Search, 
  Upload, 
  Database, 
  AlertCircle, 
  CheckCircle, 
  Loader2, 
  FileText,
  Trash2,
  Plus,
  Activity
} from "lucide-react"
import {
  colpaliSearchDocuments,
  colpaliUploadDataset,
  colpaliListCollections,
  colpaliGetCollectionInfo,
  colpaliDeleteCollection,
  colpaliCreateCollection,
  colpaliHealthCheck
} from "@/lib/api-client"
import type {
  ColPaliSearchRequest,
  ColPaliSearchResponse,
  ColPaliUploadRequest,
  ColPaliUploadResponse
} from "@/lib/api-client"

interface ColPaliState {
  collections: string[]
  searchResults: ColPaliSearchResponse | null
  selectedCollection: string
  searchQuery: string
  uploadDataset: string
  uploadCollection: string
  newCollectionName: string
  loading: {
    search: boolean
    upload: boolean
    collections: boolean
    health: boolean
  }
  error: string | null
  success: string | null
  healthStatus: boolean
}

export default function ColPaliPage() {
  const [state, setState] = useState<ColPaliState>({
    collections: [],
    searchResults: null,
    selectedCollection: "",
    searchQuery: "",
    uploadDataset: "",
    uploadCollection: "",
    newCollectionName: "",
    loading: {
      search: false,
      upload: false,
      collections: false,
      health: false
    },
    error: null,
    success: null,
    healthStatus: false
  })

  const getAuthToken = () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      throw new Error('No authentication token found')
    }
    return token
  }

  const updateState = (updates: Partial<ColPaliState>) => {
    setState(prev => ({ ...prev, ...updates }))
  }

  const updateLoading = (key: keyof ColPaliState['loading'], value: boolean) => {
    setState(prev => ({
      ...prev,
      loading: { ...prev.loading, [key]: value }
    }))
  }

  // Load collections and health status on component mount
  useEffect(() => {
    const initializeColPali = async () => {
      try {
        const token = getAuthToken()
        
        // Check health status
        updateLoading('health', true)
        try {
          await colpaliHealthCheck({
            headers: { Authorization: `Bearer ${token}` }
          })
          updateState({ healthStatus: true })
        } catch {
          updateState({ healthStatus: false })
        }
        
        // Load collections
        updateLoading('collections', true)
        const collectionsResponse = await colpaliListCollections({
          headers: { Authorization: `Bearer ${token}` }
        })
        
        if (collectionsResponse.data) {
          const collections = Array.isArray(collectionsResponse.data) ? collectionsResponse.data : []
          updateState({ 
            collections,
            selectedCollection: collections.length > 0 ? collections[0] : "",
            uploadCollection: collections.length > 0 ? collections[0] : ""
          })
        }
      } catch (error) {
        console.error('ColPali initialization error:', error)
        updateState({ error: error instanceof Error ? error.message : 'Failed to initialize ColPali' })
      } finally {
        updateLoading('health', false)
        updateLoading('collections', false)
      }
    }

    initializeColPali()
  }, [])

  const handleSearch = async () => {
    if (!state.searchQuery.trim() || !state.selectedCollection) {
      updateState({ error: 'Please enter a search query and select a collection' })
      return
    }

    try {
      updateLoading('search', true)
      updateState({ error: null, success: null })
      
      const token = getAuthToken()
      const searchRequest: ColPaliSearchRequest = {
        query: state.searchQuery,
        collection_name: state.selectedCollection,
        search_limit: 10
      }

      const response = await colpaliSearchDocuments({
        body: searchRequest,
        headers: { Authorization: `Bearer ${token}` }
      })

      if (response.data) {
        updateState({ 
          searchResults: response.data,
          success: `Found ${response.data.results?.length || 0} results`
        })
      }
    } catch (error) {
      console.error('Search error:', error)
      updateState({ error: error instanceof Error ? error.message : 'Search failed' })
    } finally {
      updateLoading('search', false)
    }
  }

  const handleUpload = async () => {
    if (!state.uploadDataset.trim() || !state.uploadCollection) {
      updateState({ error: 'Please enter a dataset name and select a collection' })
      return
    }

    try {
      updateLoading('upload', true)
      updateState({ error: null, success: null })
      
      const token = getAuthToken()
      const uploadRequest: ColPaliUploadRequest = {
        dataset_name: state.uploadDataset,
        collection_name: state.uploadCollection
      }

      const response = await colpaliUploadDataset({
        body: uploadRequest,
        headers: { Authorization: `Bearer ${token}` }
      })

      if (response.data) {
        updateState({ 
          success: response.data.message || 'Upload started successfully',
          uploadDataset: ""
        })
      }
    } catch (error) {
      console.error('Upload error:', error)
      updateState({ error: error instanceof Error ? error.message : 'Upload failed' })
    } finally {
      updateLoading('upload', false)
    }
  }

  const handleCreateCollection = async () => {
    if (!state.newCollectionName.trim()) {
      updateState({ error: 'Please enter a collection name' })
      return
    }

    try {
      updateLoading('collections', true)
      updateState({ error: null, success: null })
      
      const token = getAuthToken()
      await colpaliCreateCollection({
        path: { collection_name: state.newCollectionName },
        headers: { Authorization: `Bearer ${token}` }
      })

      // Refresh collections list
      const collectionsResponse = await colpaliListCollections({
        headers: { Authorization: `Bearer ${token}` }
      })
      
      if (collectionsResponse.data) {
        const collections = Array.isArray(collectionsResponse.data) ? collectionsResponse.data : []
        updateState({ 
          collections,
          newCollectionName: "",
          success: `Collection "${state.newCollectionName}" created successfully`
        })
      }
    } catch (error) {
      console.error('Create collection error:', error)
      updateState({ error: error instanceof Error ? error.message : 'Failed to create collection' })
    } finally {
      updateLoading('collections', false)
    }
  }

  const handleDeleteCollection = async (collectionName: string) => {
    if (!confirm(`Are you sure you want to delete the collection "${collectionName}"? This action cannot be undone.`)) {
      return
    }

    try {
      updateLoading('collections', true)
      updateState({ error: null, success: null })
      
      const token = getAuthToken()
      await colpaliDeleteCollection({
        path: { collection_name: collectionName },
        headers: { Authorization: `Bearer ${token}` }
      })

      // Refresh collections list
      const collectionsResponse = await colpaliListCollections({
        headers: { Authorization: `Bearer ${token}` }
      })
      
      if (collectionsResponse.data) {
        const collections = Array.isArray(collectionsResponse.data) ? collectionsResponse.data : []
        updateState({ 
          collections,
          selectedCollection: collections.length > 0 ? collections[0] : "",
          uploadCollection: collections.length > 0 ? collections[0] : "",
          success: `Collection "${collectionName}" deleted successfully`
        })
      }
    } catch (error) {
      console.error('Delete collection error:', error)
      updateState({ error: error instanceof Error ? error.message : 'Failed to delete collection' })
    } finally {
      updateLoading('collections', false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">ColPali Search</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Multimodal document search and management using ColPali embeddings.
        </p>
      </div>

      {/* Health Status */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center space-x-3">
            {state.loading.health ? (
              <Loader2 className="h-5 w-5 animate-spin text-gray-400" />
            ) : state.healthStatus ? (
              <CheckCircle className="h-5 w-5 text-green-500" />
            ) : (
              <AlertCircle className="h-5 w-5 text-red-500" />
            )}
            <span className="text-sm font-medium">
              ColPali Service: {state.loading.health ? 'Checking...' : state.healthStatus ? 'Online' : 'Offline'}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Error/Success Messages */}
      {state.error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{state.error}</AlertDescription>
        </Alert>
      )}

      {state.success && (
        <Alert>
          <CheckCircle className="h-4 w-4" />
          <AlertDescription>{state.success}</AlertDescription>
        </Alert>
      )}

      {/* Main Interface */}
      <Tabs defaultValue="search" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="search" className="flex items-center space-x-2">
            <Search className="h-4 w-4" />
            <span>Search</span>
          </TabsTrigger>
          <TabsTrigger value="upload" className="flex items-center space-x-2">
            <Upload className="h-4 w-4" />
            <span>Upload</span>
          </TabsTrigger>
          <TabsTrigger value="collections" className="flex items-center space-x-2">
            <Database className="h-4 w-4" />
            <span>Collections</span>
          </TabsTrigger>
        </TabsList>

        {/* Search Tab */}
        <TabsContent value="search" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Search className="h-5 w-5" />
                <span>Document Search</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="collection-select">Collection</Label>
                  <Select 
                    value={state.selectedCollection} 
                    onValueChange={(value) => updateState({ selectedCollection: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select a collection" />
                    </SelectTrigger>
                    <SelectContent>
                      {state.collections.map((collection) => (
                        <SelectItem key={collection} value={collection}>
                          {collection}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="search-query">Search Query</Label>
                  <Input
                    id="search-query"
                    placeholder="Enter your search query..."
                    value={state.searchQuery}
                    onChange={(e) => updateState({ searchQuery: e.target.value })}
                    onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  />
                </div>
              </div>
              <Button 
                onClick={handleSearch} 
                disabled={state.loading.search || !state.selectedCollection}
                className="w-full"
              >
                {state.loading.search ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Searching...
                  </>
                ) : (
                  <>
                    <Search className="mr-2 h-4 w-4" />
                    Search Documents
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Search Results */}
          {state.searchResults && (
            <Card>
              <CardHeader>
                <CardTitle>Search Results ({state.searchResults.results?.length || 0})</CardTitle>
              </CardHeader>
              <CardContent>
                {state.searchResults.results && state.searchResults.results.length > 0 ? (
                  <div className="space-y-4">
                    {state.searchResults.results.map((result, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="border rounded-lg p-4 space-y-2"
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-center space-x-2">
                            <FileText className="h-4 w-4 text-blue-500" />
                            <span className="font-medium">Document {result.id || index + 1}</span>
                          </div>
                          <Badge variant="secondary">
                            Score: {result.score?.toFixed(3) || 'N/A'}
                          </Badge>
                        </div>
                        {result.payload && (
                          <div className="text-sm text-gray-600 dark:text-gray-400">
                            <pre className="whitespace-pre-wrap">{JSON.stringify(result.payload, null, 2)}</pre>
                          </div>
                        )}
                      </motion.div>
                    ))}
                  </div>
                ) : (
                  <p className="text-center text-gray-500 dark:text-gray-400 py-8">
                    No results found. Try a different search query.
                  </p>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Upload Tab */}
        <TabsContent value="upload" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Upload className="h-5 w-5" />
                <span>Dataset Upload</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="dataset-name">Dataset Name</Label>
                  <Input
                    id="dataset-name"
                    placeholder="Enter dataset name..."
                    value={state.uploadDataset}
                    onChange={(e) => updateState({ uploadDataset: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="upload-collection">Target Collection</Label>
                  <Select 
                    value={state.uploadCollection} 
                    onValueChange={(value) => updateState({ uploadCollection: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select a collection" />
                    </SelectTrigger>
                    <SelectContent>
                      {state.collections.map((collection) => (
                        <SelectItem key={collection} value={collection}>
                          {collection}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <Button 
                onClick={handleUpload} 
                disabled={state.loading.upload || !state.uploadCollection}
                className="w-full"
              >
                {state.loading.upload ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="mr-2 h-4 w-4" />
                    Upload Dataset
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Collections Tab */}
        <TabsContent value="collections" className="space-y-6">
          {/* Create New Collection */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Plus className="h-5 w-5" />
                <span>Create New Collection</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex space-x-2">
                <Input
                  placeholder="Enter collection name..."
                  value={state.newCollectionName}
                  onChange={(e) => updateState({ newCollectionName: e.target.value })}
                  onKeyDown={(e) => e.key === 'Enter' && handleCreateCollection()}
                />
                <Button 
                  onClick={handleCreateCollection} 
                  disabled={state.loading.collections}
                >
                  {state.loading.collections ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Plus className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Collections List */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Database className="h-5 w-5" />
                <span>Existing Collections</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {state.loading.collections ? (
                <div className="space-y-3">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="flex items-center justify-between p-3 border rounded">
                      <Skeleton className="h-4 w-32" />
                      <Skeleton className="h-8 w-20" />
                    </div>
                  ))}
                </div>
              ) : state.collections.length > 0 ? (
                <div className="space-y-3">
                  {state.collections.map((collection) => (
                    <div key={collection} className="flex items-center justify-between p-3 border rounded">
                      <div className="flex items-center space-x-3">
                        <Database className="h-4 w-4 text-blue-500" />
                        <span className="font-medium">{collection}</span>
                      </div>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => handleDeleteCollection(collection)}
                        disabled={state.loading.collections}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-center text-gray-500 dark:text-gray-400 py-8">
                  No collections found. Create your first collection above.
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
