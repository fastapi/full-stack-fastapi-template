import { useUser } from "@clerk/clerk-react"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { Briefcase, Building2, Mail, Phone, User } from "lucide-react"
import { useCallback, useEffect, useState } from "react"
import { toast } from "sonner"
import { profileAPI } from "@/clients/profile"
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

export const Route = createFileRoute("/app/profile-setup")({
  component: ProfileSetup,
})

interface CompanyOption {
  company_id: string
  company_name: string
}

function ProfileSetup() {
  const navigate = useNavigate()
  const { user: clerkUser } = useUser()
  const [loading, setLoading] = useState(false)

  // Form state
  const [firstName, setFirstName] = useState("")
  const [middleName, setMiddleName] = useState("")
  const [lastName, setLastName] = useState("")
  const [phone, setPhone] = useState("")
  const [email, setEmail] = useState("")
  const [companyName, setCompanyName] = useState("")
  const [jobTitle, setJobTitle] = useState("")

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

  // Pre-fill from Clerk user data
  useEffect(() => {
    if (clerkUser) {
      if (clerkUser.primaryEmailAddress?.emailAddress) {
        setEmail(clerkUser.primaryEmailAddress.emailAddress)
      }
      if (clerkUser.firstName) {
        setFirstName(clerkUser.firstName)
      }
      if (clerkUser.lastName) {
        setLastName(clerkUser.lastName)
      }
    }
  }, [clerkUser])

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

  // Debounce effect for company search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (companyName.trim()) {
        searchCompanies(companyName)
      }
    }, 300)

    return () => clearTimeout(timer)
  }, [companyName, searchCompanies])

  const handleCompanySelect = (selectedCompany: CompanyOption) => {
    setCompanyName(selectedCompany.company_name)
    setShowCompanyDropdown(false)
    setErrors((prev) => ({ ...prev, companyName: undefined }))
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

    setLoading(true)
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

      // Update localStorage to indicate profile is complete
      localStorage.setItem("profile_complete", "true")

      // Update user object if it exists
      const userStr = localStorage.getItem("user")
      if (userStr) {
        const user = JSON.parse(userStr)
        user.profile_complete = true
        localStorage.setItem("user", JSON.stringify(user))
      }

      toast.success("Profile setup complete!")
      navigate({ to: "/app/brands" })
    } catch (error) {
      console.error("Profile setup error:", error)
      const errorMessage =
        error instanceof Error ? error.message : "Failed to set up profile"
      setErrors({ general: errorMessage })
      toast.error(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="mx-auto max-w-2xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">
            Complete Your Profile
          </h1>
          <p className="text-muted-foreground mt-2">
            Please provide your information to get started with the platform.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Profile Information
            </CardTitle>
            <CardDescription>
              Fill in your personal and company details below
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
                      First Name <span className="text-destructive">*</span>
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
                      disabled={loading}
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
                      placeholder="(Optional)"
                      disabled={loading}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="lastName">
                      Last Name <span className="text-destructive">*</span>
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
                      disabled={loading}
                      className={errors.lastName ? "border-destructive" : ""}
                    />
                    {errors.lastName && (
                      <p className="text-sm text-destructive">
                        {errors.lastName}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Contact Information Section */}
              <div className="space-y-4">
                <h3 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <Mail className="h-4 w-4" />
                  Contact Information
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="email">
                      Email <span className="text-destructive">*</span>
                    </Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
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
                        placeholder="john.doe@example.com"
                        disabled={loading}
                        className={`pl-10 ${errors.email ? "border-destructive" : ""}`}
                      />
                    </div>
                    {errors.email && (
                      <p className="text-sm text-destructive">{errors.email}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone Number</Label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        id="phone"
                        type="tel"
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        placeholder="+1 (555) 123-4567"
                        disabled={loading}
                        className="pl-10"
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Company Information Section */}
              <div className="space-y-4">
                <h3 className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <Building2 className="h-4 w-4" />
                  Company Information
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2 relative">
                    <Label htmlFor="companyName">
                      Company Name <span className="text-destructive">*</span>
                    </Label>
                    <div className="relative">
                      <Building2 className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
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
                          if (companyOptions.length > 0) {
                            setShowCompanyDropdown(true)
                          }
                        }}
                        onBlur={() => {
                          setTimeout(() => setShowCompanyDropdown(false), 200)
                        }}
                        placeholder="Enter company name"
                        disabled={loading}
                        autoComplete="off"
                        className={`pl-10 ${errors.companyName ? "border-destructive" : ""}`}
                      />
                      {searchingCompanies && (
                        <div className="absolute right-3 top-1/2 -translate-y-1/2">
                          <div className="h-4 w-4 animate-spin rounded-full border-2 border-muted-foreground border-t-primary" />
                        </div>
                      )}
                    </div>
                    {showCompanyDropdown && companyOptions.length > 0 && (
                      <div className="absolute z-10 mt-1 w-full rounded-md border bg-popover shadow-lg">
                        <ul className="max-h-48 overflow-auto py-1">
                          {companyOptions.map((opt) => (
                            <li
                              key={opt.company_id}
                              className="cursor-pointer px-3 py-2 hover:bg-accent"
                              onMouseDown={() => handleCompanySelect(opt)}
                            >
                              {opt.company_name}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {errors.companyName && (
                      <p className="text-sm text-destructive">
                        {errors.companyName}
                      </p>
                    )}
                    <p className="text-xs text-muted-foreground">
                      Start typing to search existing companies, or enter a new
                      one
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="jobTitle">Job Title</Label>
                    <div className="relative">
                      <Briefcase className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                      <Input
                        id="jobTitle"
                        type="text"
                        value={jobTitle}
                        onChange={(e) => setJobTitle(e.target.value)}
                        placeholder="e.g. Product Manager"
                        disabled={loading}
                        className="pl-10"
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Submit Button */}
              <div className="flex justify-end pt-4">
                <Button type="submit" disabled={loading} className="min-w-32">
                  {loading ? (
                    <div className="flex items-center gap-2">
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-background border-t-transparent" />
                      Saving...
                    </div>
                  ) : (
                    "Complete Setup"
                  )}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
