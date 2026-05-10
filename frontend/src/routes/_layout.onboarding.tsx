import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { ProfilesService } from "@/client"
import type { DistancePrefEnum, FitnessEnum, TerrainEnum } from "@/client"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"

export const Route = createFileRoute("/_layout/onboarding")({
  component: OnboardingPage,
  head: () => ({
    meta: [{ title: "Get Started - VNRunner" }],
  }),
})

interface OnboardingState {
  fitness_level: FitnessEnum | ""
  distance_preference: DistancePrefEnum | ""
  terrain_preference: TerrainEnum | ""
  home_city: string
}

const STEPS = ["Fitness Level", "Distance", "Terrain", "Location"] as const

const FITNESS_OPTIONS: { value: FitnessEnum; label: string; description: string }[] = [
  { value: "beginner", label: "Beginner", description: "New to running, completing 5K–10K events" },
  { value: "intermediate", label: "Intermediate", description: "Half marathon ready, regular training" },
  { value: "advanced", label: "Advanced", description: "Marathon or ultra experience" },
  { value: "elite", label: "Elite", description: "Competitive racer, podium finishes" },
]

const DISTANCE_OPTIONS: { value: DistancePrefEnum; label: string; description: string }[] = [
  { value: "short", label: "Short", description: "5K and 10K events" },
  { value: "mid", label: "Mid", description: "Half marathons (21K)" },
  { value: "long", label: "Long", description: "Full marathons (42K)" },
  { value: "ultra", label: "Ultra", description: "50K, 100K, and beyond" },
]

const TERRAIN_OPTIONS: { value: TerrainEnum; label: string; description: string }[] = [
  { value: "road", label: "Road", description: "Paved streets and city races" },
  { value: "trail", label: "Trail", description: "Mountain paths and nature runs" },
  { value: "track", label: "Track", description: "Oval track events" },
  { value: "mixed", label: "Mixed", description: "Combination of surfaces" },
]

function SelectCard<T extends string>({
  options,
  value,
  onChange,
}: {
  options: { value: T; label: string; description: string }[]
  value: T | ""
  onChange: (v: T) => void
}) {
  return (
    <div className="grid gap-3 sm:grid-cols-2">
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => onChange(opt.value)}
          className={cn(
            "rounded-lg border p-4 text-left transition-colors hover:border-primary hover:bg-primary/5",
            value === opt.value && "border-primary bg-primary/10 ring-1 ring-primary"
          )}
        >
          <div className="font-medium">{opt.label}</div>
          <div className="text-sm text-muted-foreground">{opt.description}</div>
        </button>
      ))}
    </div>
  )
}

function OnboardingPage() {
  const navigate = useNavigate()
  const [step, setStep] = useState(0)
  const [state, setState] = useState<OnboardingState>({
    fitness_level: "",
    distance_preference: "",
    terrain_preference: "",
    home_city: "",
  })

  const mutation = useMutation({
    mutationFn: () =>
      ProfilesService.upsertMyProfile({
        requestBody: {
          fitness_level: state.fitness_level || null,
          distance_preference: state.distance_preference || null,
          terrain_preference: state.terrain_preference || null,
          home_city: state.home_city || null,
          is_onboarded: true,
        },
      }),
    onSuccess: () => navigate({ to: "/" }),
  })

  const handleNext = () => {
    if (step < STEPS.length - 1) setStep(step + 1)
    else mutation.mutate()
  }

  const handleSkip = () => {
    navigate({ to: "/" })
  }

  const isLastStep = step === STEPS.length - 1

  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center p-4">
      <div className="w-full max-w-xl space-y-6">
        {/* Progress */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm text-muted-foreground">
            <span>Step {step + 1} of {STEPS.length}</span>
            <button onClick={handleSkip} className="hover:text-foreground">
              Skip setup
            </button>
          </div>
          <div className="flex gap-1">
            {STEPS.map((_, i) => (
              <div
                key={i}
                className={cn(
                  "h-1.5 flex-1 rounded-full transition-colors",
                  i <= step ? "bg-primary" : "bg-muted"
                )}
              />
            ))}
          </div>
        </div>

        <Card>
          <CardHeader>
            {step === 0 && (
              <>
                <CardTitle>What's your fitness level?</CardTitle>
                <CardDescription>We'll match races to your experience.</CardDescription>
              </>
            )}
            {step === 1 && (
              <>
                <CardTitle>Preferred race distance?</CardTitle>
                <CardDescription>Find events at the right challenge level.</CardDescription>
              </>
            )}
            {step === 2 && (
              <>
                <CardTitle>Favourite terrain?</CardTitle>
                <CardDescription>Road runner or mountain trail enthusiast?</CardDescription>
              </>
            )}
            {step === 3 && (
              <>
                <CardTitle>Where are you based?</CardTitle>
                <CardDescription>We'll show nearby races first.</CardDescription>
              </>
            )}
          </CardHeader>

          <CardContent className="space-y-4">
            {step === 0 && (
              <SelectCard
                options={FITNESS_OPTIONS}
                value={state.fitness_level}
                onChange={(v) => setState((s) => ({ ...s, fitness_level: v }))}
              />
            )}
            {step === 1 && (
              <SelectCard
                options={DISTANCE_OPTIONS}
                value={state.distance_preference}
                onChange={(v) => setState((s) => ({ ...s, distance_preference: v }))}
              />
            )}
            {step === 2 && (
              <SelectCard
                options={TERRAIN_OPTIONS}
                value={state.terrain_preference}
                onChange={(v) => setState((s) => ({ ...s, terrain_preference: v }))}
              />
            )}
            {step === 3 && (
              <input
                className="w-full rounded-md border bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="e.g. Hanoi, Ho Chi Minh City"
                value={state.home_city}
                onChange={(e) => setState((s) => ({ ...s, home_city: e.target.value }))}
              />
            )}

            <div className="flex justify-between pt-2">
              <Button
                variant="ghost"
                disabled={step === 0}
                onClick={() => setStep(step - 1)}
              >
                Back
              </Button>
              <Button onClick={handleNext} disabled={mutation.isPending}>
                {isLastStep ? (mutation.isPending ? "Saving…" : "Finish") : "Next"}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
