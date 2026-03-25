import { SignInButton, SignUpButton } from "@clerk/clerk-react"
import { Menu, X } from "lucide-react"
import { useState } from "react"
import { Button } from "@/components/ui/button"

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const products = [
    { name: "Analytics Dashboard", href: "#analytics" },
    { name: "Project Management", href: "#projects" },
    { name: "Team Collaboration", href: "#collaboration" },
    { name: "API Integration", href: "#api" },
  ]

  return (
    <header className="sticky top-0 z-50 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <img
              src="/assets/images/Kila_logo.svg"
              alt="Kila logo"
              className="h-8 w-auto"
            />
            <span className="font-display font-bold text-xl text-slate-900 dark:text-white tracking-tight">
              Kila
            </span>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            {/* Product Dropdown */}
            {/*
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
                  className="absolute top-full left-0 mt-2 w-56 bg-white dark:bg-slate-900 rounded-lg shadow-lg border border-slate-200 dark:border-slate-800 py-2"
                  onMouseEnter={() => setProductDropdownOpen(true)}
                  onMouseLeave={() => setProductDropdownOpen(false)}
                >
                  {products.map((product) => (
                    <a
                      key={product.name}
                      href={product.href}
                      className="block px-4 py-2 font-body text-sm leading-relaxed text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
                    >
                      {product.name}
                    </a>
                  ))}
                </div>
              )}
            </div>
            */}

            <a
              href="#company"
              className="font-body text-sm text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 transition"
            >
              Features
            </a>
            <a
              href="#pricing"
              className="font-body text-sm text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 transition"
            >
              Pricing
            </a>
            <a
              href="/blog"
              target="_blank"
              rel="noopener noreferrer"
              className="font-body text-sm text-slate-600 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 transition"
            >
              Blog
            </a>
          </nav>

          {/* Right Side - Auth Buttons */}
          <div className="hidden md:flex items-center space-x-4">
            <SignInButton mode="modal" forceRedirectUrl="/app/brands">
              <Button variant={"ghost"} size={"sm"}>
                Sign In
              </Button>
            </SignInButton>
            <SignUpButton mode="modal" forceRedirectUrl="/app/brands">
              <Button size={"sm"}>Sign Up Free</Button>
            </SignUpButton>
          </div>

          {/* Mobile menu button */}
          <button
            type="button"
            className="md:hidden text-slate-700 dark:text-slate-300"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-slate-200 dark:border-slate-800">
            <nav className="flex flex-col space-y-4">
              <div className="space-y-2">
                <div className="font-body font-medium text-xs tracking-[0.2em] uppercase text-slate-500 dark:text-slate-400 px-2">
                  Products
                </div>
                {products.map((product) => (
                  <a
                    key={product.name}
                    href={product.href}
                    className="block px-4 py-2 font-body text-sm leading-relaxed text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition"
                  >
                    {product.name}
                  </a>
                ))}
              </div>
              <a
                href="#company"
                className="px-2 font-body text-sm text-slate-700 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 transition"
              >
                Company
              </a>
              <a
                href="#pricing"
                className="px-2 font-body text-sm text-slate-700 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 transition"
              >
                Pricing
              </a>
              <a
                href="/blog"
                target="_blank"
                rel="noopener noreferrer"
                className="px-2 font-body text-sm text-slate-700 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400 transition"
              >
                Blog
              </a>
              <SignInButton mode="modal" forceRedirectUrl="/app/brands">
                <Button variant={"ghost"}>Sign In</Button>
              </SignInButton>
              <SignUpButton mode="modal" forceRedirectUrl="/app/brands">
                <Button>Sign Up Free</Button>
              </SignUpButton>
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}
