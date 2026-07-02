import { HeroSection } from "@/components/ui/hero-section-1"

interface DemoProps {
  onEnter?: () => void;
}

export function Demo ({ onEnter }: DemoProps) {
  return (
    <HeroSection onEnterPlatform={onEnter} />
  )
}
