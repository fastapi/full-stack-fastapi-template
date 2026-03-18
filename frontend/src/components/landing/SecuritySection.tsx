import { Shield, Lock, Database, CheckCircle } from "lucide-react"

const securityFeatures = [
  {
    icon: Shield,
    title: "Enterprise-Grade Security",
    description: "Built with security-first architecture to protect your sensitive data",
  },
  {
    icon: Lock,
    title: "SOC 2 Compliant",
    description: "Independently audited and certified for data protection standards",
  },
  {
    icon: Database,
    title: "Data Encryption",
    description: "End-to-end encryption ensures your data is always secure",
  },
  {
    icon: CheckCircle,
    title: "Privacy First",
    description: "We never share your data. Your insights stay yours.",
  },
]

export default function SecuritySection() {
  return (
    <section className="relative py-20 bg-white">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute top-0 left-0 w-[400px] h-[400px] bg-blue-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-green-500/5 rounded-full blur-3xl" />
      </div>
      
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <p className="font-body text-xs font-semibold uppercase tracking-[0.25em] text-blue-600 mb-4">
            Security & Trust
          </p>
          <h2 className="font-display font-bold text-3xl sm:text-4xl tracking-tight text-slate-900">
            Your Data is Safe with Kila
          </h2>
          <p className="font-body text-base text-slate-600 mt-4 max-w-2xl mx-auto">
            We take security seriously. Your brand data is protected by enterprise-grade measures
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {securityFeatures.map((feature, idx) => (
            <div
              key={idx}
              className="text-center p-6"
            >
              <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center">
                <feature.icon className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="font-display font-semibold text-lg text-slate-900 mb-2">
                {feature.title}
              </h3>
              <p className="font-body text-sm text-slate-600">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* Trust badges */}
        <div className="mt-12 flex flex-wrap justify-center items-center gap-8 opacity-60">
          <div className="flex items-center gap-2 text-slate-500">
            <Shield className="h-5 w-5" />
            <span className="font-body text-sm font-medium">SOC 2 Type II</span>
          </div>
          <div className="flex items-center gap-2 text-slate-500">
            <Lock className="h-5 w-5" />
            <span className="font-body text-sm font-medium">256-bit Encryption</span>
          </div>
          <div className="flex items-center gap-2 text-slate-500">
            <Database className="h-5 w-5" />
            <span className="font-body text-sm font-medium">GDPR Compliant</span>
          </div>
        </div>
      </div>
    </section>
  )
}