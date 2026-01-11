import { cn } from '@/lib/utils';

export function AiPersona({ isSpeaking }: { isSpeaking?: boolean }) {
  return (
    <div
      className={cn(
        "relative w-40 h-40 md:w-48 md:h-48 flex items-center justify-center",
        isSpeaking && "animate-[pulse-ring_2s_ease-in-out_infinite]"
      )}
    >
      <div
        className="absolute inset-0 rounded-full animate-[hue-rotate_8s_linear_infinite]"
        style={{ background: 'var(--ring-gradient)' }}
      />
      <div className="absolute inset-1 rounded-full bg-background" />
      <span className="relative text-4xl font-bold tracking-widest uppercase text-foreground">
        HUE
      </span>
    </div>
  );
}
