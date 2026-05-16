/**
 * SEO and AIO (AI Optimization) utilities
 * Provides helpers for meta tags, structured data, and AI-friendly content
 */

interface SEOMetaTags {
  title: string
  description: string
  keywords?: string
  canonicalUrl?: string
  ogImage?: string
  ogType?: "website" | "article" | "event"
  twitterCard?: "summary" | "summary_large_image"
  author?: string
  publishedTime?: string
  modifiedTime?: string
}

/**
 * Generate comprehensive meta tags for SEO and social sharing
 */
export function generateMetaTags(config: SEOMetaTags) {
  const baseUrl = import.meta.env.VITE_FRONTEND_URL || "https://vnrunner.com"
  const siteName = "VNRunner"
  const defaultImage = `${baseUrl}/assets/images/og-default.jpg`

  return [
    // Basic meta tags
    { title: config.title },
    { name: "description", content: config.description },
    ...(config.keywords ? [{ name: "keywords", content: config.keywords }] : []),
    { name: "author", content: config.author || siteName },
    
    // Open Graph (Facebook, LinkedIn, etc.)
    { property: "og:site_name", content: siteName },
    { property: "og:title", content: config.title },
    { property: "og:description", content: config.description },
    { property: "og:type", content: config.ogType || "website" },
    { property: "og:image", content: config.ogImage || defaultImage },
    { property: "og:image:alt", content: config.title },
    ...(config.canonicalUrl ? [{ property: "og:url", content: config.canonicalUrl }] : []),
    
    // Twitter Cards
    { name: "twitter:card", content: config.twitterCard || "summary_large_image" },
    { name: "twitter:title", content: config.title },
    { name: "twitter:description", content: config.description },
    { name: "twitter:image", content: config.ogImage || defaultImage },
    
    // Article specific (if applicable)
    ...(config.publishedTime ? [{ property: "article:published_time", content: config.publishedTime }] : []),
    ...(config.modifiedTime ? [{ property: "article:modified_time", content: config.modifiedTime }] : []),
    
    // Additional SEO
    { name: "robots", content: "index, follow" },
    { name: "googlebot", content: "index, follow" },
  ]
}

/**
 * Generate JSON-LD structured data for Schema.org
 */
export interface OrganizationSchema {
  name: string
  url: string
  logo: string
  description: string
  sameAs?: string[]
}

export function generateOrganizationSchema(config: OrganizationSchema) {
  return {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: config.name,
    url: config.url,
    logo: config.logo,
    description: config.description,
    ...(config.sameAs && { sameAs: config.sameAs }),
  }
}

export interface EventSchema {
  name: string
  description: string
  startDate: string
  endDate?: string
  location: {
    name: string
    address?: {
      streetAddress?: string
      addressLocality?: string
      addressRegion?: string
      addressCountry?: string
    }
    geo?: {
      latitude: number
      longitude: number
    }
  }
  image?: string
  organizer?: {
    name: string
    url?: string
  }
  offers?: {
    price: number
    priceCurrency: string
    availability: "InStock" | "SoldOut" | "PreOrder"
    url?: string
    validFrom?: string
  }[]
}

export function generateEventSchema(config: EventSchema) {
  return {
    "@context": "https://schema.org",
    "@type": "SportsEvent",
    name: config.name,
    description: config.description,
    startDate: config.startDate,
    ...(config.endDate && { endDate: config.endDate }),
    location: {
      "@type": "Place",
      name: config.location.name,
      ...(config.location.address && {
        address: {
          "@type": "PostalAddress",
          ...config.location.address,
        },
      }),
      ...(config.location.geo && {
        geo: {
          "@type": "GeoCoordinates",
          latitude: config.location.geo.latitude,
          longitude: config.location.geo.longitude,
        },
      }),
    },
    ...(config.image && { image: config.image }),
    ...(config.organizer && {
      organizer: {
        "@type": "Organization",
        name: config.organizer.name,
        ...(config.organizer.url && { url: config.organizer.url }),
      },
    }),
    ...(config.offers && {
      offers: config.offers.map((offer) => ({
        "@type": "Offer",
        price: offer.price,
        priceCurrency: offer.priceCurrency,
        availability: `https://schema.org/${offer.availability}`,
        ...(offer.url && { url: offer.url }),
        ...(offer.validFrom && { validFrom: offer.validFrom }),
      })),
    }),
  }
}

export interface BreadcrumbItem {
  name: string
  url: string
}

export function generateBreadcrumbSchema(items: BreadcrumbItem[]) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      item: item.url,
    })),
  }
}

export interface FAQItem {
  question: string
  answer: string
}

export function generateFAQSchema(items: FAQItem[]) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: items.map((item) => ({
      "@type": "Question",
      name: item.question,
      acceptedAnswer: {
        "@type": "Answer",
        text: item.answer,
      },
    })),
  }
}

/**
 * Component to inject JSON-LD structured data
 */
export function StructuredData({ data }: { data: object }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  )
}

/**
 * Strip HTML tags for meta descriptions
 */
export function stripHtml(html: string): string {
  const tmp = document.createElement("DIV")
  tmp.innerHTML = html
  return tmp.textContent || tmp.innerText || ""
}

/**
 * Truncate text to specified length with ellipsis
 */
export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength - 3) + "..."
}
