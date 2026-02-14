/**
 * UserProfile Component
 *
 * Displays and allows editing of the current user's profile information.
 * Features:
 * - View mode by default (all fields read-only)
 * - Edit button to enable editing
 * - Personal information: First name, Middle name, Last name, Phone, Email
 * - Company information: Company name, Job title
 * - Loads existing profile data from backend
 */

import { Briefcase, Building2, Loader2, Mail, Pencil, Phone, User } from "lucide-react"
import { useCallback, useEffect, useState } from "react"
import { toast } from "sonner"
import { profileAPI, type ProfileResponse } from "@/clients/profile"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface CompanyOption {
  company_id: string
  company_name: string
}

export default function UserProfile() {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [isEditMode, setIsEditMode] = useState(false)
  const [loadError, setLoadError] = useState<string | null>(null)

  // Form state
  const [firstName, setFirstName] = useState("")
  const [middleName, setMiddleName] = useState("")
  const [lastName, setLastName] = useState("")
  const [phone, setPhone] = useState("")
  const [email, setEmail] = useState("")
  const [companyName, setCompanyName] = useState("")
  const [jobTitle, setJobTitle] = useState("")

  // Original data for cancel/reset
  const [originalData, setOriginalData] = useState<{
    firstName: string
    middleName: string
    lastName: string
    phone: string
    email: string
    companyName: string
    jobTitle: string
  } | null>(null)

  // Company autocomplete state
  const [companyOptions, setCompanyOptions] = useState<CompanyOption[]>([])
  const [showCompanyDropdown, setShowCompanyDropdown] = useState(false)
  const [searchingCompanies, setSearchingCompanies] = useState(false)

  // Error state
  const [errors, setErrors] = useState<{
    firstName?: string
    lastName?: string
    email?: string
    companyName?: string
    general?: string
  }>({})

  // Load profile on mount
  useEffect(() => {
    const loadProfile = async () => {
      try {
        setLoading(true)
        setLoadError(null)

        const profile: ProfileResponse | null = await profileAPI.getProfile()

        if (profile) {
          const data = {
            firstName: profile.first_name || "",
            middleName: profile.middle_name || "",
            lastName: profile.last_name || "",
            phone: profile.phone || "",
            email: profile.email || "",
            companyName: profile.company?.company_name || "",
            jobTitle: profile.job_title || "",
          }

          setFirstName(data.firstName)
          setMiddleName(data.middleName)
          setLastName(data.lastName)
          setPhone(data.phone)
          setEmail(data.email)
          setCompanyName(data.companyName)
          setJobTitle(data.jobTitle)
          setOriginalData(data)
        }
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Failed to load profile"
        setLoadError(errorMessage)
        console.error("[UserProfile] Error loading profile:", err)
      } finally {
        setLoading(false)
      }
    }

    loadProfile()
  }, [])

  // Debounced company search
  const searchCompanies = useCallback(async (query: string) => {
    if (query.length < 1) {
      setCompanyOptions([])
      setShowCompanyDropdown(false)
      return
    }

    setSearchingCompanies(true)
    try {
      const results = await profileAPI.searchCompanies(query)
      setCompanyOptions(results)
      setShowCompanyDropdown(results.length > 0)
    } catch {
      setCompanyOptions([])
    } finally {
      setSearchingCompanies(false)
    }
  }, [])

  // Debounce effect for company search (only when in edit mode)
  useEffect(() => {
    if (!isEditMode) return

    const timer = setTimeout(() => {
      if (companyName.trim()) {
        searchCompanies(companyName)
      }
    }, 300)

    return () => clearTimeout(timer)
  }, [companyName, searchCompanies, isEditMode])

  const handleCompanySelect = (selectedCompany: CompanyOption) => {
    setCompanyName(selectedCompany.company_name)
    setShowCompanyDropdown(false)
    setErrors((prev) => ({ ...prev, companyName: undefined }))
  }

  const handleEnableEdit = () => {
    setIsEditMode(true)
  }

  const handleCancelEdit = () => {
    if (originalData) {
      setFirstName(originalData.firstName)
      setMiddleName(originalData.middleName)
      setLastName(originalData.lastName)
      setPhone(originalData.phone)
      setEmail(originalData.email)
      setCompanyName(originalData.companyName)
      setJobTitle(originalData.jobTitle)
    }
    setIsEditMode(false)
    setErrors({})
    setShowCompanyDropdown(false)
  }

  const validateForm = () => {
    const newErrors: typeof errors = {}

    if (!firstName.trim()) {
      newErrors.firstName = "First name is required"
    }

    if (!lastName.trim()) {
      newErrors.lastName = "Last name is required"
    }

    if (!email.trim()) {
      newErrors.email = "Email is required"
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = "Please enter a valid email address"
    }

    if (!companyName.trim()) {
      newErrors.companyName = "Company name is required"
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) {
      return
    }

    setSaving(true)
    setErrors({})

    try {
      await profileAPI.setupProfile({
        first_name: firstName.trim(),
        middle_name: middleName.trim() || undefined,
        last_name: lastName.trim(),
        phone: phone.trim() || undefined,
        email: email.trim(),
        company_name: companyName.trim(),
        job_title: jobTitle.trim() || undefined,
      })

      // Update original data
      setOriginalData({
        firstName: firstName.trim(),
        middleName: middleName.trim(),
        lastName: lastName.trim(),
        phone: phone.trim(),
        email: email.trim(),
        companyName: companyName.trim(),
        jobTitle: jobTitle.trim(),
      })

      toast.success("Profile updated successfully!")
      setIsEditMode(false)
    } catch (error) {
      console.error("Profile update error:", error)
      const errorMessage =
        error instanceof Error ? error.message : "Failed to update profile"
      setErrors({ general: errorMessage })
      toast.error(errorMessage)
    } finally {
      setSaving(false)
    }
  }

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="mx-auto max-w-2xl">
          <Card>
            <CardContent className="flex flex-col items-center justify-center h-64">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
              <p className="mt-4 text-sm text-gray-500">Loading profile...</p>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  // Error state
  if (loadError) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="mx-auto max-w-2xl">
          <Card>
            <CardContent className="flex flex-col items-center justify-center h-64">
              <div className="text-red-500 text-center">
                <p className="font-medium">Failed to load profile</p>
                <p className="text-sm mt-2">{loadError}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="mx-auto max-w-2xl">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">My Profile</h1>
            <p className="text-muted-foreground mt-2">
              View and manage your profile information.
            </p>
          </div>
          {!isEditMode && (
            <Button variant="outline" onClick={handleEnableEdit}>
              <Pencil className="h-4 w-4 mr-2" />
              Edit
            </Button>
          )}
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Profile Information
            </CardTitle>
            <CardDescription>
              {isEditMode
                ? "Update your personal and company details below"
                : "Your personal and company details"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {errors.general && (
                <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
                  {errors.general}
                </div>
              )}

              {/* Personal Information Section */}
              <div className="space-y-4">
                <h3 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <User className="h-4 w-4" />
                  Personal Information
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="firstName">
                      First Name {isEditMode && <span className="text-destructive">*</span>}
                    </Label>
                    <Input
                      id="firstName"
                      type="text"
                      value={firstName}
                      onChange={(e) => {
                        setFirstName(e.target.value)
                        if (errors.firstName) {
                          setErrors((prev) => ({
                            ...prev,
                            firstName: undefined,
                          }))
                        }
                      }}
                      placeholder="John"
                      disabled={!isEditMode || saving}
                      className={errors.firstName ? "border-destructive" : ""}
                    />
                    {errors.firstName && (
                      <p className="text-sm text-destructive">
                        {errors.firstName}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="middleName">Middle Name</Label>
                    <Input
                      id="middleName"
                      type="text"
                      value={middleName}
                      onChange={(e) => setMiddleName(e.target.value)}
                      disabled={!isEditMode || saving}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="lastName">
                      Last Name {isEditMode && <span className="text-destructive">*</span>}
                    </Label>
                    <Input
                      id="lastName"
                      type="text"
                      value={lastName}
                      onChange={(e) => {
                        setLastName(e.target.value)
                        if (errors.lastName) {
                          setErrors((prev) => ({
                            ...prev,
                            lastName: undefined,
                          }))
                        }
                      }}
                      placeholder="Doe"
                      disabled={!isEditMode || saving}
                      className={errors.lastName ? "border-destructive" : ""}
                    />
                    {errors.lastName && (
                      <p className="text-sm text-destructive">
                        {errors.lastName}
                      </p>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label
                      htmlFor="phone"
                      className="flex items-center gap-2"
                    >
                      <Phone className="h-4 w-4" />
                      Phone Number
                    </Label>
                    <Input
                      id="phone"
                      type="tel"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      placeholder="+1 (555) 000-0000"
                      disabled={!isEditMode || saving}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label
                      htmlFor="email"
                      className="flex items-center gap-2"
                    >
                      <Mail className="h-4 w-4" />
                      Email {isEditMode && <span className="text-destructive">*</span>}
                    </Label>
                    <Input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => {
                        setEmail(e.target.value)
                        if (errors.email) {
                          setErrors((prev) => ({ ...prev, email: undefined }))
                        }
                      }}
                      placeholder="john@example.com"
                      disabled={!isEditMode || saving}
                      className={errors.email ? "border-destructive" : ""}
                    />
                    {errors.email && (
                      <p className="text-sm text-destructive">{errors.email}</p>
                    )}
                  </div>
                </div>
              </div>

              {/* Company Information Section */}
              <div className="space-y-4 pt-4 border-t">
                <h3 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <Building2 className="h-4 w-4" />
                  Company Information
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2 relative">
                    <Label
                      htmlFor="companyName"
                      className="flex items-center gap-2"
                    >
                      <Building2 className="h-4 w-4" />
                      Company Name {isEditMode && <span className="text-destructive">*</span>}
                    </Label>
                    <Input
                      id="companyName"
                      type="text"
                      value={companyName}
                      onChange={(e) => {
                        setCompanyName(e.target.value)
                        if (errors.companyName) {
                          setErrors((prev) => ({
                            ...prev,
                            companyName: undefined,
                          }))
                        }
                      }}
                      onFocus={() => {
                        if (isEditMode && companyOptions.length > 0) {
                          setShowCompanyDropdown(true)
                        }
                      }}
                      placeholder="Acme Corporation"
                      disabled={!isEditMode || saving}
                      className={errors.companyName ? "border-destructive" : ""}
                      autoComplete="off"
                    />
                    {errors.companyName && (
                      <p className="text-sm text-destructive">
                        {errors.companyName}
                      </p>
                    )}
                    {/* Company Autocomplete Dropdown */}
                    {isEditMode && showCompanyDropdown && companyOptions.length > 0 && (
                      <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-md shadow-lg max-h-60 overflow-auto">
                        {companyOptions.map((option) => (
                          <button
                            key={option.company_id}
                            type="button"
                            className="w-full px-4 py-2 text-left hover:bg-gray-100 focus:bg-gray-100 focus:outline-none"
                            onClick={() => handleCompanySelect(option)}
                          >
                            {option.company_name}
                          </button>
                        ))}
                      </div>
                    )}
                    {isEditMode && searchingCompanies && (
                      <p className="text-xs text-muted-foreground mt-1">
                        Searching...
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label
                      htmlFor="jobTitle"
                      className="flex items-center gap-2"
                    >
                      <Briefcase className="h-4 w-4" />
                      Job Title
                    </Label>
                    <Input
                      id="jobTitle"
                      type="text"
                      value={jobTitle}
                      onChange={(e) => setJobTitle(e.target.value)}
                      placeholder="Software Engineer"
                      disabled={!isEditMode || saving}
                    />
                  </div>
                </div>
              </div>

              {/* Action Buttons - only show in edit mode */}
              {isEditMode && (
                <div className="flex justify-end gap-3 pt-4 border-t">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleCancelEdit}
                    disabled={saving}
                  >
                    Cancel
                  </Button>
                  <Button type="submit" disabled={saving}>
                    {saving ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      "Save Changes"
                    )}
                  </Button>
                </div>
              )}
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
