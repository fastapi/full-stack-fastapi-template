import { createFileRoute, Link } from "@tanstack/react-router"
import { ArrowRight, Calendar, MapPin, Trophy, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { RaceCard } from "@/components/Races/RaceCard"
import { useRaceSearch } from "@/hooks/useRaceSearch"
import { isLoggedIn } from "@/hooks/useAuth"
import { generateMetaTags, generateOrganizationSchema, StructuredData } from "@/lib/seo"

const baseUrl = import.meta.env.VITE_FRONTEND_URL || "https://vnrunner.com"

export const Route = createFileRoute("/_public/")({
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

const features = [
  {
    icon: Calendar,
    title: "Discover Races",
    description:
      "Browse upcoming races in your area and find the perfect event for your goals.",
  },
  {
    icon: MapPin,
    title: "Easy Registration",
    description:
      "Register online in minutes with our simple and secure registration process.",
  },
  {
    icon: Trophy,
    title: "Track Progress",
    description:
      "View your race history, track your PRs, and celebrate your achievements.",
  },
]

function HorizontalRail({
  title,
  link,
  races,
  isLoading,
}: {
  title: string
  link?: string
  races: { id: string; [key: string]: unknown }[]
  isLoading: boolean
}) {
  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">{title}</h2>
        {link && (
          <Link
            to="/races"
            className="flex items-center gap-1 text-sm text-primary hover:underline"
          >
            View all <ChevronRight className="size-4" />
          </Link>
        )}
      </div>
      {isLoading ? (
        <div className="flex gap-4 overflow-x-auto pb-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <div
              key={i}
              className="h-56 w-72 shrink-0 rounded-lg border bg-muted/50 animate-pulse"
            />
          ))}
        </div>
      ) : races.length === 0 ? (
        <p className="text-sm text-muted-foreground py-4">No races to show right now.</p>
      ) : (
        <div className="flex gap-4 overflow-x-auto pb-2 snap-x">
          {races.map((race) => (
            <div key={race.id} className="w-72 shrink-0 snap-start">
              <RaceCard race={race as Parameters<typeof RaceCard>[0]["race"]} />
            </div>
          ))}
        </div>
      )}
    </section>
  )
}

function PersonalizedSections() {
  const { data: trendingData, isLoading: trendingLoading } = useRaceSearch({
    sort: "popularity",
    limit: 6,
  })
  const { data: upcomingData, isLoading: upcomingLoading } = useRaceSearch({
    sort: "date",
    limit: 6,
  })

  return (
    <div className="space-y-10">
      <HorizontalRail
        title="Trending Races"
        link="/races?sort=popularity"
        races={trendingData?.data ?? []}
        isLoading={trendingLoading}
      />
      <HorizontalRail
        title="Upcoming Races"
        link="/races?sort=date"
        races={upcomingData?.data ?? []}
        isLoading={upcomingLoading}
      />
    </div>
  )
}

function HomePage() {
  const loggedIn = isLoggedIn()

  const organizationSchema = generateOrganizationSchema({
    name: "VNRunner",
    url: baseUrl,
    logo: `${baseUrl}/assets/images/favicon.png`,
    description: "Vietnam's premier platform for discovering and registering for running races, trail runs, and marathons.",
    sameAs: [
      // Add social media URLs when available
      // "https://facebook.com/vnrunner",
      // "https://instagram.com/vnrunner",
    ],
  })

  return (
    <>
      <StructuredData data={organizationSchema} />
      
      {/* Hero Section */}
      <section className="w-full py-16 md:py-24 lg:py-32" itemScope itemType="https://schema.org/WebSite">
        <meta itemProp="url" content={baseUrl} />
        <meta itemProp="name" content="VNRunner" />
        <div className="container">
          <div className="mx-auto max-w-3xl text-center space-y-8">
            <h1 className="text-4xl font-bold tracking-tight md:text-5xl lg:text-6xl">
              Find Your Next Vietnamese Race
            </h1>
            <p className="text-lg text-muted-foreground md:text-xl">
              Discover trail runs, road races and ultras across Vietnam. Join
              thousands of runners achieving their goals.
            </p>
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
              <Button size="lg" asChild>
                <Link to="/races">
                  Browse Races <ArrowRight className="ml-2 size-4" />
                </Link>
              </Button>
              {!loggedIn && (
                <Button size="lg" variant="outline" asChild>
                  <Link to="/signup">Create Account</Link>
                </Button>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Race rails */}
      <section className="w-full py-12 md:py-16">
        <div className="container">
          <div className="mx-auto max-w-7xl">
            <PersonalizedSections />
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="w-full bg-muted/50 py-16 md:py-24">
        <div className="container">
          <div className="mx-auto max-w-2xl text-center space-y-4 mb-12">
            <h2 className="text-3xl font-bold tracking-tight md:text-4xl">
              Why Choose VNRunner?
            </h2>
            <p className="text-lg text-muted-foreground">
              Everything you need to find, register, and prepare for your next
              running event in Vietnam.
            </p>
          </div>
          <div className="mx-auto grid max-w-5xl gap-6 md:grid-cols-3">
            {features.map(({ icon: Icon, title, description }) => (
              <Card
                key={title}
                className="border-2 transition-shadow hover:shadow-lg"
              >
                <CardHeader className="space-y-4">
                  <div className="flex size-12 items-center justify-center rounded-lg bg-primary/10">
                    <Icon className="size-6 text-primary" />
                  </div>
                  <CardTitle className="text-xl">{title}</CardTitle>
                  <CardDescription className="text-base">
                    {description}
                  </CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section (unauthenticated only) */}
      {!loggedIn && (
        <section className="w-full py-16 md:py-24">
          <div className="container">
            <div className="mx-auto max-w-4xl">
              <Card className="border-2 bg-muted/50">
                <CardContent className="p-8 text-center md:p-12">
                  <div className="mx-auto max-w-2xl space-y-6">
                    <h2 className="text-2xl font-bold tracking-tight md:text-3xl">
                      Ready to Start Running?
                    </h2>
                    <p className="text-lg text-muted-foreground">
                      Create your free account today and get personalised race
                      recommendations.
                    </p>
                    <Button size="lg" asChild>
                      <Link to="/signup">Get Started Free</Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>
      )}
    </>
  )
}

export default HomePage
