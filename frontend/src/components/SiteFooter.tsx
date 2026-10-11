import { Link } from "@tanstack/react-router";

export function SiteFooter() {
  return (
    <footer className="border-t border-border/60 bg-background">
      <div className="mx-auto grid max-w-7xl gap-10 px-6 py-16 md:grid-cols-3 lg:px-10">
        <div>
          <p className="font-display text-2xl tracking-[0.3em] text-cream">PANTHERA®</p>
          <p className="mt-4 max-w-xs text-sm leading-relaxed text-muted-foreground">
            A conservation research platform identifying individual leopards through their
            unique rosette patterns.
          </p>
        </div>
        <div>
          <p className="eyebrow">Platform</p>
          <div className="mt-4 flex flex-col gap-2 text-sm text-cream/75">
            <Link to="/vision-ai" className="hover:text-primary">
              Analyse
            </Link>
            <Link to="/ivp-system" className="hover:text-primary">
              Pipeline
            </Link>
            <Link to="/research" className="hover:text-primary">
              Research
            </Link>
            <Link to="/reach-us" className="hover:text-primary">
              Reach Us
            </Link>
          </div>
        </div>
        <div>
          <p className="eyebrow">Field Office</p>
          <p className="mt-4 text-sm leading-relaxed text-muted-foreground">
            Africa Field Research Station
            <br />
            field@panthera.org
          </p>
        </div>
      </div>
      <div className="border-t border-border/60 px-6 py-6 text-center text-xs tracking-[0.2em] text-muted-foreground lg:px-10">
        © 2026 PANTHERA RESEARCH COLLECTIVE
      </div>
    </footer>
  );
}
