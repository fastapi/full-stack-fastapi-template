import { createFileRoute, Link } from "@tanstack/react-router"
import { ArrowRight, Calendar, MapPin, Trophy } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export const Route = createFileRoute("/_public/")({
  component: HomePage,
  head: () => ({
    meta: [
      {
        title: "RaceHub - Find and Register for Running Races",
        description:
          "Discover running races near you. Register online, track your progress, and join a community of runners.",
      },
    ],
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

function HomePage() {
  return (
    <>
      {/* Hero Section */}
      <section className="w-full py-16 md:py-24 lg:py-32">
        <div className="container">
          <div className="mx-auto max-w-3xl text-center space-y-8">
            <h1 className="text-4xl font-bold tracking-tight md:text-5xl lg:text-6xl">
              Find Your Next Race
            </h1>
            <p className="text-lg text-muted-foreground md:text-xl">
              Discover and register for running races near you. Join thousands
              of runners achieving their goals.
            </p>
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
              <Button size="lg" asChild>
                <Link to="/races">
                  Browse Races <ArrowRight className="ml-2 size-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <Link to="/signup">Create Account</Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="w-full bg-muted/50 py-16 md:py-24">
        <div className="container">
          <div className="mx-auto max-w-2xl text-center space-y-4 mb-12">
            <h2 className="text-3xl font-bold tracking-tight md:text-4xl">
              Why Choose RaceHub?
            </h2>
            <p className="text-lg text-muted-foreground">
              Everything you need to find, register, and prepare for your next
              running event.
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

      {/* CTA Section */}
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
                    Create your free account today and get access to hundreds of
                    races in your area.
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
    </>
  )
}

export default HomePage
