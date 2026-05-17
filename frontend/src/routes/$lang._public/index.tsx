import { createFileRoute, Link } from "@tanstack/react-router"
import { ArrowRight, Sparkles } from "lucide-react"
import { useTranslation } from "react-i18next"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { RaceCard } from "@/components/Races/RaceCard"
import { PublicFooter } from "@/components/Public/PublicFooter"
import { useRaceSearch } from "@/hooks/useRaceSearch"
import { isLoggedIn } from "@/hooks/useAuth"
import { generateMetaTags, generateOrganizationSchema, StructuredData } from "@/lib/seo"

const baseUrl = import.meta.env.VITE_FRONTEND_URL || "https://vnrunner.com"

export const Route = createFileRoute("/$lang/_public/")({
  component: HomePage,
  head: () => ({
    meta: generateMetaTags({
      title: "VNRunner - Discover Vietnamese Running Races & Trail Runs | Register Online",
      description:
        "Find and register for running races across Vietnam. Discover trail runs, road races, marathons, and ultras. Join thousands of Vietnamese runners achieving their goals. Free online registration.",
      keywords: "Vietnam running races, trail running Vietnam, marathon Vietnam, ultra running, race registration, Vietnamese runners, running events Vietnam, 5K 10K races Vietnam",
      canonicalUrl: baseUrl,
      ogType: "website",
    }),
  }),
})

function HomePage() {
  const loggedIn = isLoggedIn()
  const { i18n } = useTranslation()
  const { lang } = Route.useParams()
  const currentLang = lang || i18n.language || "vi"
  const [searchQuery, setSearchQuery] = useState("")

  // Fetch hand-picked races
  const { data: handPickedData, isLoading } = useRaceSearch({
    sort: "popularity",
    limit: 6,
  })
  const handPickedRaces = handPickedData?.data ?? []
  const totalRaces = handPickedData?.count ?? 11248

  const organizationSchema = generateOrganizationSchema({
    name: "VNRunner",
    url: baseUrl,
    logo: `${baseUrl}/assets/images/favicon.png`,
    description: "Vietnam's premier platform for discovering and registering for running races, trail runs, and marathons.",
    sameAs: [],
  })

  const quickFilters = [
    "search half marathons in October",
    "flat fast 10K near me",
    "cool weather marathons",
    "find ultras under 50K",
  ]

  const handleSearch = () => {
    // Navigate to races page with search query
    if (searchQuery.trim()) {
      window.location.href = `/${currentLang}/races?q=${encodeURIComponent(searchQuery)}`
    }
  }

  return (
    <>
      <StructuredData data={organizationSchema} />
      
      {/* Hero Section - Bold Typography with AI Search */}
      <section className="w-full py-16 md:py-20 lg:py-24" itemScope itemType="https://schema.org/WebSite">
        <meta itemProp="url" content={baseUrl} />
        <meta itemProp="name" content="VNRunner" />
        <div className="container max-w-[1100px]">
          <div className="mx-auto text-center space-y-5">
            {/* Small header text with icon */}
            <div className="flex items-center justify-center gap-2 text-xs tracking-[0.14em] uppercase text-[#74716A] font-mono">
              <Sparkles className="size-3.5" />
              <span>THE AI RACE FINDER · {totalRaces.toLocaleString()} RACES INDEXED</span>
            </div>
            
            {/* Large bold heading - Anton-style */}
            <h1 className="text-6xl md:text-8xl lg:text-[168px] font-black tracking-[-0.01em] leading-[0.9] uppercase">
              Find your
              <br />
              <span className="text-[#FF5A1F]">next</span> start
              <br />
              line.
            </h1>
            
            {/* Subtitle */}
            <p className="text-lg md:text-xl text-[#74716A] max-w-[620px] mx-auto leading-7">
              Describe what you want — terrain, weather, distance, vibe — and we'll find the races that fit.
            </p>
            
            {/* AI Search Bar */}
            <div className="max-w-[820px] mx-auto space-y-4 pt-5">
              <div className="relative bg-white border-2 border-[#E6E1D7] rounded-[28px] shadow-[0px_6px_12px_rgba(15,14,12,0.06),0px_1px_1px_rgba(15,14,12,0.04)] p-2.5">
                <div className="flex items-center gap-3 px-4">
                  <Sparkles className="size-3.5 text-[#74716A] flex-shrink-0" />
                  <Input
                    type="text"
                    placeholder='Ask anything — "half marathon in October, cool weather, scenic"'
                    className="flex-1 h-11 px-1 border-0 text-base focus-visible:ring-0 focus-visible:ring-offset-0 shadow-none"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                  />
                  <Button
                    onClick={handleSearch}
                    className="rounded-full h-11 px-5 font-bold text-sm bg-[#FF5A1F] hover:bg-[#FF5A1F]/90"
                  >
                    Find races <ArrowRight className="ml-2 size-4" />
                  </Button>
                </div>
              </div>
              
              {/* Quick filters */}
              <div className="flex flex-wrap items-center justify-center gap-2">
                <span className="text-xs text-[#74716A] font-mono tracking-widest uppercase">Try:</span>
                {quickFilters.map((filter) => (
                  <Badge
                    key={filter}
                    variant="outline"
                    className="cursor-pointer hover:bg-muted/50 transition-colors rounded-full px-3 py-1.5 border-[#E6E1D7] text-xs font-bold"
                    onClick={() => setSearchQuery(filter)}
                  >
                    {filter}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Hand-Picked Races Section */}
      <section className="w-full py-16 md:py-20 lg:py-24">
        <div className="container max-w-[1400px]">
          <div className="space-y-7">
            {/* Section header with border */}
            <div className="flex items-end justify-between pb-7 border-b-2 border-[#0F0E0C]">
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs tracking-[0.14em] uppercase text-[#74716A] font-mono">
                  <Sparkles className="size-3.5" />
                  <span>RECOMMENDED FOR YOU</span>
                </div>
                <h2 className="text-4xl md:text-5xl lg:text-[56px] font-black tracking-tight leading-[0.92] uppercase">
                  Hand-picked races.
                </h2>
              </div>
              <Link
                to="/$lang/races"
                params={{ lang: currentLang }}
                className="text-sm font-bold hover:text-primary transition-colors flex items-center gap-2 border border-[#E6E1D7] rounded-full px-5 py-2.5"
              >
                See all <ArrowRight className="size-4" />
              </Link>
            </div>
            
            {/* Races Grid */}
            {isLoading ? (
              <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                {Array.from({ length: 6 }).map((_, i) => (
                  <div
                    key={i}
                    className="h-[331px] rounded-[22px] border border-[#E6E1D7] bg-card/50 animate-pulse"
                  />
                ))}
              </div>
            ) : handPickedRaces.length > 0 ? (
              <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                {handPickedRaces.map((race) => (
                  <RaceCard key={race.id} race={race} />
                ))}
              </div>
            ) : (
              <p className="text-center text-muted-foreground py-12">
                No races available at the moment.
              </p>
            )}
          </div>
        </div>
      </section>

      {/* CTA Section - Orange Background */}
      {loggedIn && (
        <section className="w-full py-16 md:py-20 bg-[#FF5A1F] relative overflow-hidden">
          {/* Decorative elements */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-0 right-0 w-96 h-96 bg-white rounded-full blur-3xl" />
            <div className="absolute bottom-0 left-0 w-96 h-96 bg-white rounded-full blur-3xl" />
          </div>
          
          <div className="container max-w-[1328px] relative">
            <div className="grid lg:grid-cols-[1.4fr_1fr] gap-12 items-center">
              {/* Left side - Copy */}
              <div className="space-y-3">
                <p className="text-xs tracking-[0.14em] uppercase text-white/70 font-mono">
                  FREE FOREVER · NO CREDIT CARD
                </p>
                <h2 className="text-5xl md:text-6xl lg:text-[80px] font-black tracking-tight leading-[0.95] uppercase text-white">
                  Save races.
                  <br />
                  Get smarter
                  <br />
                  recommendations.
                </h2>
                <p className="text-base leading-6 text-white/90 max-w-[680px]">
                  Sign up to save races, build a season calendar, get personalized AI picks, and never miss a registration window.
                </p>
              </div>
                
              {/* Right side - Form */}
              <div className="bg-white rounded-[22px] p-6 space-y-2.5">
                <p className="text-xs tracking-[0.14em] uppercase text-[#74716A] font-mono">
                  Start in 30 seconds
                </p>
                
                <Input
                  type="email"
                  placeholder="your@email.com"
                  className="h-12 rounded-full border-[#E6E1D7] text-sm"
                />
                
                <Button className="w-full h-11 rounded-full bg-[#0F0E0C] hover:bg-[#0F0E0C]/90 text-white font-bold text-sm">
                  Create free account <ArrowRight className="ml-2 size-4" />
                </Button>
                
                <div className="flex items-center gap-2 py-1">
                  <div className="flex-1 h-px bg-[#E6E1D7]" />
                  <span className="text-xs text-[#74716A]">OR</span>
                  <div className="flex-1 h-px bg-[#E6E1D7]" />
                </div>
                
                <div className="grid grid-cols-2 gap-2 pt-1">
                  <Button variant="outline" className="h-[34px] rounded-full border-[#E6E1D7] text-xs font-bold">
                    Apple
                  </Button>
                  <Button variant="outline" className="h-[34px] rounded-full border-[#E6E1D7] text-xs font-bold">
                    Google
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </section>
      )}
    </>
  )
}
