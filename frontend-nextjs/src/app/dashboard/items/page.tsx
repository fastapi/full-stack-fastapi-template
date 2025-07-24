"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Plus, MoreHorizontal, Edit, Trash2, Search, Loader2, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination"
import {
  itemsReadItems,
  itemsCreateItem,
  itemsUpdateItem,
  itemsDeleteItem
} from "@/lib/api-client"
import type { ItemPublic, ItemCreate, ItemUpdate } from "@/client/types.gen"

interface ItemsState {
  items: ItemPublic[]
  totalCount: number
  currentPage: number
  loading: boolean
  error: string | null
  success: string | null
}

interface ItemFormData {
  title: string
  description: string
}

const PER_PAGE = 5

export default function ItemsPage() {
  const [state, setState] = useState<ItemsState>({
    items: [],
    totalCount: 0,
    currentPage: 1,
    loading: true,
    error: null,
    success: null
  })
  
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [editingItem, setEditingItem] = useState<ItemPublic | null>(null)
  const [formData, setFormData] = useState<ItemFormData>({ title: "", description: "" })
  const [formLoading, setFormLoading] = useState(false)

  const getAuthToken = () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      throw new Error('No authentication token found')
    }
    return token
  }

  const updateState = (updates: Partial<ItemsState>) => {
    setState(prev => ({ ...prev, ...updates }))
  }

  const fetchItems = async (page: number = 1) => {
    try {
      updateState({ loading: true, error: null })
      const token = getAuthToken()
      
      const response = await itemsReadItems({
        query: {
          skip: (page - 1) * PER_PAGE,
          limit: PER_PAGE
        },
        headers: { Authorization: `Bearer ${token}` }
      })

      if (response.data) {
        updateState({
          items: response.data.data || [],
          totalCount: response.data.count || 0,
          currentPage: page,
          loading: false
        })
      }
    } catch (error) {
      console.error('Fetch items error:', error)
      updateState({
        error: error instanceof Error ? error.message : 'Failed to fetch items',
        loading: false
      })
    }
  }

  useEffect(() => {
    fetchItems()
  }, [])

  const handleCreateItem = async () => {
    if (!formData.title.trim()) {
      updateState({ error: 'Title is required' })
      return
    }

    try {
      setFormLoading(true)
      updateState({ error: null, success: null })
      const token = getAuthToken()
      
      const itemData: ItemCreate = {
        title: formData.title,
        description: formData.description || undefined
      }

      await itemsCreateItem({
        body: itemData,
        headers: { Authorization: `Bearer ${token}` }
      })

      updateState({ success: 'Item created successfully' })
      setFormData({ title: "", description: "" })
      setIsAddDialogOpen(false)
      fetchItems(state.currentPage)
    } catch (error) {
      console.error('Create item error:', error)
      updateState({ error: error instanceof Error ? error.message : 'Failed to create item' })
    } finally {
      setFormLoading(false)
    }
  }

  const handleUpdateItem = async () => {
    if (!editingItem || !formData.title.trim()) {
      updateState({ error: 'Title is required' })
      return
    }

    try {
      setFormLoading(true)
      updateState({ error: null, success: null })
      const token = getAuthToken()
      
      const itemData: ItemUpdate = {
        title: formData.title,
        description: formData.description || undefined
      }

      await itemsUpdateItem({
        path: { id: editingItem.id.toString() },
        body: itemData,
        headers: { Authorization: `Bearer ${token}` }
      })

      updateState({ success: 'Item updated successfully' })
      setFormData({ title: "", description: "" })
      setIsEditDialogOpen(false)
      setEditingItem(null)
      fetchItems(state.currentPage)
    } catch (error) {
      console.error('Update item error:', error)
      updateState({ error: error instanceof Error ? error.message : 'Failed to update item' })
    } finally {
      setFormLoading(false)
    }
  }

  const handleDeleteItem = async (item: ItemPublic) => {
    if (!confirm(`Are you sure you want to delete "${item.title}"? This action cannot be undone.`)) {
      return
    }

    try {
      updateState({ error: null, success: null })
      const token = getAuthToken()
      
      await itemsDeleteItem({
        path: { id: item.id.toString() },
        headers: { Authorization: `Bearer ${token}` }
      })

      updateState({ success: 'Item deleted successfully' })
      fetchItems(state.currentPage)
    } catch (error) {
      console.error('Delete item error:', error)
      updateState({ error: error instanceof Error ? error.message : 'Failed to delete item' })
    }
  }

  const openEditDialog = (item: ItemPublic) => {
    setEditingItem(item)
    setFormData({ title: item.title, description: item.description || "" })
    setIsEditDialogOpen(true)
  }

  const openAddDialog = () => {
    setFormData({ title: "", description: "" })
    setIsAddDialogOpen(true)
  }

  const totalPages = Math.ceil(state.totalCount / PER_PAGE)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Items Management</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage your application items and their properties.
          </p>
        </div>
        <Button onClick={openAddDialog} className="flex items-center space-x-2">
          <Plus className="h-4 w-4" />
          <span>Add Item</span>
        </Button>
      </div>

      {/* Error/Success Messages */}
      {state.error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{state.error}</AlertDescription>
        </Alert>
      )}

      {state.success && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{state.success}</AlertDescription>
        </Alert>
      )}

      {/* Items Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Search className="h-5 w-5" />
            <span>Items ({state.totalCount})</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {state.loading ? (
            <div className="space-y-3">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="flex items-center space-x-4">
                  <Skeleton className="h-4 w-16" />
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-4 w-48" />
                  <Skeleton className="h-4 w-20" />
                </div>
              ))}
            </div>
          ) : state.items.length === 0 ? (
            <div className="text-center py-12">
              <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                No items found
              </h3>
              <p className="text-gray-500 dark:text-gray-400 mb-4">
                Get started by creating your first item.
              </p>
              <Button onClick={openAddDialog}>
                <Plus className="h-4 w-4 mr-2" />
                Add Item
              </Button>
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Title</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {state.items.map((item, index) => (
                    <motion.tr
                      key={item.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="border-b"
                    >
                      <TableCell className="font-mono text-sm">{item.id}</TableCell>
                      <TableCell className="font-medium">{item.title}</TableCell>
                      <TableCell className="text-gray-600 dark:text-gray-400 max-w-xs truncate">
                        {item.description || (
                          <span className="italic text-gray-400">No description</span>
                        )}
                      </TableCell>
                      <TableCell className="text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-8 w-8 p-0">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => openEditDialog(item)}>
                              <Edit className="mr-2 h-4 w-4" />
                              Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem 
                              onClick={() => handleDeleteItem(item)}
                              className="text-red-600"
                            >
                              <Trash2 className="mr-2 h-4 w-4" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </motion.tr>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex justify-center mt-6">
                  <Pagination>
                    <PaginationContent>
                      <PaginationItem>
                        <PaginationPrevious 
                          onClick={() => state.currentPage > 1 && fetchItems(state.currentPage - 1)}
                          className={state.currentPage <= 1 ? "pointer-events-none opacity-50" : "cursor-pointer"}
                        />
                      </PaginationItem>
                      {[...Array(totalPages)].map((_, i) => {
                        const page = i + 1
                        if (page === state.currentPage) {
                          return (
                            <PaginationItem key={page}>
                              <PaginationLink isActive>{page}</PaginationLink>
                            </PaginationItem>
                          )
                        }
                        return (
                          <PaginationItem key={page}>
                            <PaginationLink 
                              onClick={() => fetchItems(page)}
                              className="cursor-pointer"
                            >
                              {page}
                            </PaginationLink>
                          </PaginationItem>
                        )
                      })}
                      <PaginationItem>
                        <PaginationNext 
                          onClick={() => state.currentPage < totalPages && fetchItems(state.currentPage + 1)}
                          className={state.currentPage >= totalPages ? "pointer-events-none opacity-50" : "cursor-pointer"}
                        />
                      </PaginationItem>
                    </PaginationContent>
                  </Pagination>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Add Item Dialog */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add New Item</DialogTitle>
            <DialogDescription>
              Create a new item with a title and optional description.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="add-title">Title *</Label>
              <Input
                id="add-title"
                placeholder="Enter item title..."
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="add-description">Description</Label>
              <Textarea
                id="add-description"
                placeholder="Enter item description..."
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateItem} disabled={formLoading}>
              {formLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Creating...
                </>
              ) : (
                'Create Item'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Item Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Item</DialogTitle>
            <DialogDescription>
              Update the item's title and description.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="edit-title">Title *</Label>
              <Input
                id="edit-title"
                placeholder="Enter item title..."
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-description">Description</Label>
              <Textarea
                id="edit-description"
                placeholder="Enter item description..."
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdateItem} disabled={formLoading}>
              {formLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Updating...
                </>
              ) : (
                'Update Item'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
