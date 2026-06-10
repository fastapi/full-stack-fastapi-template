import { setRequestLocale } from "next-intl/server";
import Background from "@/components/sections/Background";
import Nav from "@/components/sections/Nav";
import Hero from "@/components/sections/Hero";
import HowItWorks from "@/components/sections/HowItWorks";
import Features from "@/components/sections/Features";
import Stats from "@/components/sections/Stats";
import FinalCTA from "@/components/sections/FinalCTA";
import Footer from "@/components/sections/Footer";

export default function LandingPage({ params: { locale } }: { params: { locale: string } }) {
  setRequestLocale(locale);
  return (
    <div className="landing">
      <Background />
      <Nav />
      <Hero />
      <HowItWorks />
      <Features />
      <Stats />
      <FinalCTA />
      <Footer />
    </div>
  );
}
