import * as Dialog from "@radix-ui/react-dialog"
import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"
import FileUploadZone from "@/components/FileUploadZone"
import FAQ from "@/components/faq"
import Features from "@/components/features"
import Footer from "@/components/footer"
import Header from "@/components/header"
import Hero from "@/components/hero"
import HowItWorks from "@/components/how-it-works"
import Testimonials from "@/components/testimonials"
import { Button } from "@/components/ui/button"

export const Route = createFileRoute("/_public/")({
  component: Home,
  head: () => ({
    meta: [{ title: "BankToExcel - Convert Bank Statements to Excel" }],
  }),
})
function Home() {
  const [isOpen, setIsOpen] = useState(false)
  const [fileName, setFileName] = useState<string | null>(null)
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <Hero />
      <Features />
      <HowItWorks />
      <Testimonials />
      <FAQ />
      <Footer />

      <Dialog.Root open={isOpen} onOpenChange={setIsOpen}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 z-50 bg-black/50" />
          <Dialog.Content className="fixed left-1/2 top-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-lg bg-card p-8 shadow-xl">
            <Dialog.Title className="text-2xl font-bold text-card-foreground">
              Upload Bank Statement
            </Dialog.Title>
            <Dialog.Description className="mt-2 text-sm text-muted-foreground">
              Upload a PDF or image of your bank statement to convert to Excel
              (up to 100 MB)
            </Dialog.Description>

            <FileUploadZone onFileSelect={(file) => setFileName(file.name)} />

            {fileName && (
              <div className="mt-6 space-y-4">
                <div className="rounded-lg bg-secondary p-4">
                  <p className="text-sm font-medium text-card-foreground">
                    Selected file:{" "}
                    <span className="text-primary">{fileName}</span>
                  </p>
                </div>
                <Button className="w-full rounded-lg bg-primary px-4 py-2 font-semibold text-primary-foreground hover:bg-primary/90 transition-colors">
                  Convert to Excel
                </Button>
              </div>
            )}

            <Dialog.Close asChild>
              <button
                type="button"
                className="absolute right-4 top-4 text-muted-foreground hover:text-foreground transition-colors"
                aria-label="Close"
              >
                <svg
                  className="h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <title>Close dialog</title>
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </Dialog.Close>
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </div>
  )
}
