import { createFileRoute } from "@tanstack/react-router"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export const Route = createFileRoute("/_public/about")({
  component: AboutPage,
  head: () => ({
    meta: [
      {
        title: "About Us - RaceHub",
        description:
          "Learn more about RaceHub and our mission to connect runners with races.",
      },
    ],
  }),
})

function AboutPage() {
  return (
    <div className="w-full py-8 md:py-12">
      <div className="container">
        <div className="mx-auto max-w-4xl space-y-8">
          {/* Header */}
          <div className="space-y-4">
            <h1 className="text-3xl font-bold tracking-tight md:text-4xl">
              About RaceHub
            </h1>
            <p className="text-lg text-muted-foreground leading-relaxed">
              RaceHub is your go-to platform for discovering and registering for
              running races. We connect runners with race organizers to create
              memorable racing experiences.
            </p>
          </div>

          {/* Mission Card */}
          <Card className="border-2">
            <CardHeader className="space-y-2">
              <CardTitle className="text-2xl">Our Mission</CardTitle>
              <CardDescription className="text-base">
                Making race discovery and registration simple for everyone
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground leading-relaxed">
                We believe running brings people together. Our platform makes it
                easy to find races that match your goals, register securely
                online, and track your running journey. Whether you're training
                for your first 5K or your tenth marathon, RaceHub helps you find
                the perfect event.
              </p>
            </CardContent>
          </Card>

          {/* Features Grid */}
          <div className="grid gap-6 md:grid-cols-2">
            <Card className="border-2">
              <CardHeader>
                <CardTitle className="text-xl">For Runners</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 text-muted-foreground">
                  <li className="flex gap-3">
                    <span className="mt-1 text-primary">•</span>
                    <span>Browse races by distance, location, and date</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="mt-1 text-primary">•</span>
                    <span>Register online with secure payment processing</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="mt-1 text-primary">•</span>
                    <span>Track your race history and personal records</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="mt-1 text-primary">•</span>
                    <span>Receive race updates and important information</span>
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border-2">
              <CardHeader>
                <CardTitle className="text-xl">For Race Organizers</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 text-muted-foreground">
                  <li className="flex gap-3">
                    <span className="mt-1 text-primary">•</span>
                    <span>
                      Create and manage races with our intuitive dashboard
                    </span>
                  </li>
                  <li className="flex gap-3">
                    <span className="mt-1 text-primary">•</span>
                    <span>
                      Process registrations and participant management
                    </span>
                  </li>
                  <li className="flex gap-3">
                    <span className="mt-1 text-primary">•</span>
                    <span>Access real-time registration data and reports</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="mt-1 text-primary">•</span>
                    <span>
                      Communicate with participants before and after the race
                    </span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AboutPage
