import { ChevronDown, Menu, X } from "lucide-react"
import { useState } from "react"
import { Button } from "@/components/ui/button"

interface HeaderProps {
  onOpenAuth: (mode: "signin" | "signup") => void
}

export default function Header({ onOpenAuth }: HeaderProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [productDropdownOpen, setProductDropdownOpen] = useState(false)

  const products = [
    { name: "Analytics Dashboard", href: "#analytics" },
    { name: "Project Management", href: "#projects" },
    { name: "Team Collaboration", href: "#collaboration" },
    { name: "API Integration", href: "#api" },
  ]

  return (
    <header className="sticky top-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">K</span>
              </div>
              <span className="text-xl font-bold text-gray-900 dark:text-white">
                Kila
              </span>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            {/* Product Dropdown */}
            <div className="relative">
              <Button
                variant={"ghost"}
                onMouseEnter={() => setProductDropdownOpen(true)}
                onMouseLeave={() => setProductDropdownOpen(false)}
              >
                <span>Products</span>
                <ChevronDown size={16} />
              </Button>

              {productDropdownOpen && (
                <div
                  className="absolute top-full left-0 mt-2 w-56 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-2"
                  onMouseEnter={() => setProductDropdownOpen(true)}
                  onMouseLeave={() => setProductDropdownOpen(false)}
                >
                  {products.map((product) => (
                    <a
                      key={product.name}
                      href={product.href}
                      className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition"
                    >
                      {product.name}
                    </a>
                  ))}
                </div>
              )}
            </div>

            <a
              href="#company"
              className="font-display text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition"
            >
              Company
            </a>
            <a
              href="#pricing"
              className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition"
            >
              Pricing
            </a>
          </nav>

          {/* Right Side - Auth Buttons */}
          <div className="hidden md:flex items-center space-x-4">
            <Button
              onClick={() => onOpenAuth("signin")}
              variant={"ghost"}
              size={"sm"}
            >
              Sign In
            </Button>
            <Button onClick={() => onOpenAuth("signup")} size={"sm"}>
              Sign Up Free
            </Button>
          </div>

          {/* Mobile menu button */}
          <button
            className="md:hidden text-gray-700 dark:text-gray-300"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-gray-200 dark:border-gray-800">
            <nav className="flex flex-col space-y-4">
              <div className="space-y-2">
                <div className="text-sm font-semibold text-gray-500 dark:text-gray-400 px-2">
                  Products
                </div>
                {products.map((product) => (
                  <a
                    key={product.name}
                    href={product.href}
                    className="block px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition"
                  >
                    {product.name}
                  </a>
                ))}
              </div>
              <a
                href="#company"
                className="px-2 text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition"
              >
                Company
              </a>
              <a
                href="#pricing"
                className="px-2 text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition"
              >
                Pricing
              </a>
              <Button variant={"ghost"} onClick={() => onOpenAuth("signin")}>
                Sign In
              </Button>
              <Button onClick={() => onOpenAuth("signup")}>Sign Up Free</Button>
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}
