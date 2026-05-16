import { createFileRoute } from "@tanstack/react-router"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { generateMetaTags, generateFAQSchema, StructuredData } from "@/lib/seo"

const baseUrl = import.meta.env.VITE_FRONTEND_URL || "https://vnrunner.com"

export const Route = createFileRoute("/_public/about")({
  component: AboutPage,
  head: () => ({
    meta: generateMetaTags({
      title: "About VNRunner - Vietnam's Premier Running Race Platform",
      description:
        "Learn about VNRunner's mission to connect Vietnamese runners with races. Discover our platform features for runners and race organizers. Join thousands of runners finding their perfect race.",
      keywords: "about VNRunner, running platform Vietnam, race registration platform, Vietnamese running community",
      canonicalUrl: `${baseUrl}/about`,
    }),
  }),
})

function AboutPage() {
  const faqSchema = generateFAQSchema([
    {
      question: "What is VNRunner?",
      answer: "VNRunner is Vietnam's premier platform for discovering and registering for running races. We connect runners with race organizers to create memorable racing experiences across Vietnam.",
    },
    {
      question: "How do I register for a race?",
      answer: "Browse our race listings, select your preferred event, and complete the online registration form. Payment is processed securely through our platform. You'll receive confirmation and race details via email.",
    },
    {
      question: "Can race organizers use VNRunner?",
      answer: "Yes! Race organizers can create and manage races through our intuitive dashboard, process registrations, access participant data, and communicate with runners before and after events.",
    },
    {
      question: "What types of races are available?",
      answer: "VNRunner features a variety of races including road races, trail runs, marathons, half marathons, ultramarathons, 5K, 10K events, and more across Vietnam.",
    },
  ])

  return (
    <div className="w-full py-8 md:py-12">
      <StructuredData data={faqSchema} />
      <div className="container">
        <article className="mx-auto max-w-4xl space-y-8" itemScope itemType="https://schema.org/AboutPage">
          <meta itemProp="name" content="About VNRunner" />
          {/* Header */}
          <header className="space-y-4">
            <h1 className="text-3xl font-bold tracking-tight md:text-4xl" itemProp="headline">
              About VNRunner
            </h1>
            <p className="text-lg text-muted-foreground leading-relaxed" itemProp="description">
              VNRunner is your go-to platform for discovering and registering for
              running races across Vietnam. We connect runners with race organizers to create
              memorable racing experiences.
            </p>
          </header>

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
        </article>
      </div>
    </div>
  )
}

export default AboutPage
