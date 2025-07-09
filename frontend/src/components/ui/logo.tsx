import { cn } from "@/lib/utils"
import Image from "next/image"

interface LogoProps {
  className?: string
  size?: "sm" | "md" | "lg"
  variant?: "icon" | "full"
}

export function Logo({ className, size = "md", variant = "icon" }: LogoProps) {
  const sizeClasses = {
    sm: "h-6 w-6",
    md: "h-8 w-8", 
    lg: "h-12 w-12"
  }

  const fullSizeClasses = {
    sm: "h-6 w-auto",
    md: "h-8 w-auto",
    lg: "h-10 w-auto"
  }

  if (variant === "full") {
    return (
      <div className={cn("flex items-center", className)}>
        <Image
          src="/logo-large.svg"
          alt="SCADA Industrial Control"
          width={120}
          height={40}
          className={cn(fullSizeClasses[size])}
          priority
        />
      </div>
    )
  }

  return (
    <div className={cn("flex items-center justify-center", className)}>
      <Image
        src="/logo.svg"
        alt="SCADA"
        width={32}
        height={32}
        className={cn(sizeClasses[size])}
        priority
      />
    </div>
  )
} 