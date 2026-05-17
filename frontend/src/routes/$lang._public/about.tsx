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

export const Route = createFileRoute("/$lang/_public/about")({
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
    <div className="w-full py-12 md:py-16 lg:py-20">
      <StructuredData data={faqSchema} />
      <div className="container">
        <article className="mx-auto max-w-4xl space-y-12" itemScope itemType="https://schema.org/AboutPage">
          <meta itemProp="name" content="About VNRunner" />
          {/* Header */}
          <header className="space-y-6 text-center">
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight" itemProp="headline">
              About VNRunner
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground leading-relaxed max-w-3xl mx-auto" itemProp="description">
              VNRunner is your go-to platform for discovering and registering for
              running races across Vietnam. We connect runners with race organizers to create
              memorable racing experiences.
            </p>
          </header>

          {/* Mission Card */}
          <Card className="border border-primary/20 bg-gradient-to-br from-card to-card/50 backdrop-blur rounded-2xl">
            <CardHeader className="space-y-3 p-8">
              <CardTitle className="text-3xl font-bold">Our Mission</CardTitle>
              <CardDescription className="text-lg">
                Making race discovery and registration simple for everyone
              </CardDescription>
            </CardHeader>
            <CardContent className="px-8 pb-8">
              <p className="text-muted-foreground leading-relaxed text-lg">
                We believe running brings people together. Our platform makes it
                easy to find races that match your goals, register securely
                online, and track your running journey. Whether you're training
                for your first 5K or your tenth marathon, VNRunner helps you find
                the perfect event.
              </p>
            </CardContent>
          </Card>

          {/* Features Grid */}
          <div className="grid gap-8 md:grid-cols-2">
            <Card className="border border-border/50 bg-card/50 backdrop-blur-sm rounded-2xl transition-all hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5">
              <CardHeader className="p-8">
                <CardTitle className="text-2xl font-semibold">For Runners</CardTitle>
              </CardHeader>
              <CardContent className="px-8 pb-8">
                <ul className="space-y-4 text-muted-foreground">
                  <li className="flex gap-3">
                    <span className="mt-1 text-primary font-bold">•</span>
                    <span className="leading-relaxed">Browse races by distance, location, and date</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="mt-1 text-primary font-bold">•</span>
                    <span className="leading-relaxed">Register online with secure payment processing</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="mt-1 text-primary font-bold">•</span>
                    <span className="leading-relaxed">Track your race history and personal records</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="mt-1 text-primary font-bold">•</span>
                    <span className="leading-relaxed">Receive race updates and important information</span>
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card className="border border-border/50 bg-card/50 backdrop-blur-sm rounded-2xl transition-all hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5">
              <CardHeader className="p-8">
                <CardTitle className="text-2xl font-semibold">For Race Organizers</CardTitle>
              </CardHeader>
              <CardContent className="px-8 pb-8">
                <ul className="space-y-4 text-muted-foreground">
                  <li className="flex gap-3">
                    <span className="mt-1 text-primary font-bold">•</span>
                    <span className="leading-relaxed">
                      Create and manage races with our intuitive dashboard
                    </span>
                  </li>
                  <li className="flex gap-3">
                    <span className="mt-1 text-primary font-bold">•</span>
                    <span className="leading-relaxed">
                      Process registrations and participant management
                    </span>
                  </li>
                  <li className="flex gap-3">
                    <span className="mt-1 text-primary font-bold">•</span>
                    <span className="leading-relaxed">Access real-time registration data and reports</span>
                  </li>
                  <li className="flex gap-3">
                    <span className="mt-1 text-primary font-bold">•</span>
                    <span className="leading-relaxed">
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
