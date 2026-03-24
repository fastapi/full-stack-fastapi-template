import { Eye, Swords, TrendingUp } from "lucide-react"

interface Feature {
  title: string
  description: string
  img: string
}

interface Category {
  id: string
  icon: React.ElementType
  label: string
  heading: string
  tagline: string
  accent: {
    badge: string
    border: string
    heading: string
    dot: string
  }
  features: Feature[]
}

const categories: Category[] = [
  {
    id: "impression",
    icon: Eye,
    label: "Brand Impression",
    heading: "Know exactly how AI sees your brand.",
    tagline:
      "Track visibility, ranking, sentiment, and the sources AI cites — updated daily so you always have a clear picture.",
    accent: {
      badge: "bg-blue-50 text-blue-700",
      border: "border-blue-200",
      heading: "text-blue-700",
      dot: "bg-blue-500",
    },
    features: [
      {
        title: "Historical Trend",
        description:
          "Visualise how your AI visibility, ranking, and sentiment have moved over time. Spot inflection points before they become business problems.",
        img: "/assets/features/Impression_historical_trend.png",
      },
      {
        title: "Ranking Details",
        description:
          "Drill into best, worst, average, and median ranking positions across every query. Understand the spread — not just the average.",
        img: "/assets/features/Impression_ranking_details.png",
      },
      {
        title: "AI Reference Sources",
        description:
          "See every source AI systems cite when surfacing your brand. Identify which third-party sites drive your authority and which are missing.",
        img: "/assets/features/Impression_reference_sources.png",
      },
      {
        title: "Sentiment Analysis",
        description:
          "Read the AI-sourced customer reviews that shape buyer perception — filtered by positive and negative so you can act on what matters.",
        img: "/assets/features/Impression_sentiments.png",
      },
    ],
  },
  {
    id: "competitive",
    icon: Swords,
    label: "Competitive Analysis",
    heading: "See exactly where you win — and where you lose.",
    tagline:
      "Compare ranking gaps, citation sources, and customer sentiment side-by-side against every competitor tracked by AI.",
    accent: {
      badge: "bg-indigo-50 text-indigo-700",
      border: "border-indigo-200",
      heading: "text-indigo-700",
      dot: "bg-indigo-500",
    },
    features: [
      {
        title: "Ranking Gap Analysis",
        description:
          "Compare best, worst, and average ranking positions against competitors over time. Know at a glance whether you're gaining or losing ground.",
        img: "/assets/features/competitive_gaps_ranking.png",
      },
      {
        title: "Gap Historical Trend",
        description:
          "Track how the gap in visibility, median ranking, and sentiment between you and competitors has evolved — so you can catch displacement early.",
        img: "/assets/features/competitive_gaps_visibility_sentiment.png",
      },
      {
        title: "Sentiment Comparison",
        description:
          "Read AI-collected customer reviews for you and your competitors side by side. Understand the narrative difference that moves buyers.",
        img: "/assets/features/competitive_sentiment_comparison.png",
      },
      {
        title: "Reference Source Comparison",
        description:
          "Discover which sources AI uses for competitors but not for you — and which sources you share. Close the citation gap strategically.",
        img: "/assets/features/competitive_sources_comparison.png",
      },
    ],
  },
  {
    id: "market",
    icon: TrendingUp,
    label: "Market Dynamic",
    heading: "Track the market before it moves against you.",
    tagline:
      "Understand category-level momentum, visibility share, and position strength so you can act on market shifts weeks before they hit revenue.",
    accent: {
      badge: "bg-sky-50 text-sky-700",
      border: "border-sky-200",
      heading: "text-sky-700",
      dot: "bg-sky-500",
    },
    features: [
      {
        title: "Competitive Matrix",
        description:
          "Plot every brand by average visibility share and position strength on a single chart. Instantly see who dominates, who is emerging, and where you sit.",
        img: "/assets/features/market_competitive_matrix.png",
      },
      {
        title: "Position Strength Trends",
        description:
          "Track how each brand's AI position strength evolves week over week. Spot momentum swings before they compound into permanent share loss.",
        img: "/assets/features/market_position_strength.png",
      },
      {
        title: "Visibility Share History",
        description:
          "Watch market visibility redistribute across all tracked brands over time. A rising competitor shows up here weeks before it shows up in revenue.",
        img: "/assets/features/market_visibility_history.png",
      },
      {
        title: "Current Visibility Share",
        description:
          "A clean snapshot of today's AI visibility distribution across the full competitive set — who owns the shelf and who is being squeezed out.",
        img: "/assets/features/market_visibility_share.png",
      },
    ],
  },
]

function FeatureCard({ feature }: { feature: Feature }) {
  return (
    <div className="group/card flex flex-col rounded-2xl border border-slate-200 bg-white overflow-hidden hover:border-slate-300 hover:shadow-[0_12px_40px_-12px_rgba(15,23,42,0.18)] transition-all duration-300">
      {/* Screenshot */}
      <div className="relative overflow-hidden bg-slate-50 border-b border-slate-100">
        <img
          src={feature.img}
          alt={feature.title}
          className="w-full object-cover object-top group-hover/card:scale-[1.02] transition-transform duration-500"
          style={{ maxHeight: "200px" }}
        />
      </div>
      {/* Text */}
      <div className="p-5 flex flex-col gap-1.5 flex-1">
        <h4 className="font-display font-semibold text-sm text-slate-900">
          {feature.title}
        </h4>
        <p className="font-body text-xs text-slate-500 leading-relaxed">
          {feature.description}
        </p>
      </div>
    </div>
  )
}

function CategorySection({ cat }: { cat: Category }) {
  const Icon = cat.icon
  return (
    <div className="mt-20">
      {/* Category header */}
      <div
        className={`rounded-2xl border ${cat.accent.border} bg-white px-6 py-6 sm:px-8 mb-6`}
      >
        <div className="flex items-start gap-4">
          <div
            className={`flex-shrink-0 flex items-center justify-center w-10 h-10 rounded-xl ${cat.accent.badge}`}
          >
            <Icon className="h-5 w-5" />
          </div>
          <div>
            <span
              className={`inline-block text-xs font-semibold uppercase tracking-[0.2em] ${cat.accent.heading} mb-1`}
            >
              {cat.label}
            </span>
            <h3 className="font-display font-bold text-xl sm:text-2xl tracking-tight text-slate-900 leading-snug">
              {cat.heading}
            </h3>
            <p className="font-body text-sm text-slate-500 mt-1.5 max-w-2xl">
              {cat.tagline}
            </p>
          </div>
        </div>
      </div>
      {/* 2-column feature grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {cat.features.map((feature) => (
          <FeatureCard key={feature.title} feature={feature} />
        ))}
      </div>
    </div>
  )
}

export default function ProductSection() {
  return (
    <section className="relative py-24 bg-white">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-32 left-[-10%] h-[420px] w-[420px] rounded-full bg-blue-500/10 blur-3xl" />
        <div className="absolute top-[35%] right-[-15%] h-[460px] w-[460px] rounded-full bg-sky-400/10 blur-3xl" />
      </div>
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Row 1 — Problem statement (unchanged) */}
        <div className="rounded-3xl border border-slate-200 bg-slate-50 px-6 py-10 sm:px-10">
          <p className="font-body text-xs font-semibold uppercase tracking-[0.25em] text-slate-500">
            The Problem
          </p>
          <h2 className="font-display font-bold text-3xl sm:text-4xl tracking-tight text-slate-900 mt-4">
            AI answers are quietly redirecting your customers to competitors —
            you won't even know you're losing without AI visibility.
          </h2>
          <p className="font-body text-sm text-slate-600 mt-4 max-w-3xl">
            Traditional SEO doesn't reveal how AI systems rank, cite, and
            describe your brand. Kila makes AI search performance measurable.
          </p>
        </div>

        {/* Feature categories */}
        {categories.map((cat) => (
          <CategorySection key={cat.id} cat={cat} />
        ))}
      </div>
    </section>
  )
}
