import Image from "next/image";
import { ChartNoAxesCombined, ChevronRight, Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import type { ForecastRecommendation } from "@/features/agent/agent-stream";
import { formatPhp } from "@/lib/utils";

type FxPilotRecommendationProps = {
  className?: string;
  recommendation: ForecastRecommendation | null;
};

export function FxPilotRecommendation({ className, recommendation }: FxPilotRecommendationProps) {
  const summary = recommendation
    ? `${recommendation.recommended_day} is the recommended day for ${formatPhp(recommendation.amount_php)} through ${recommendation.provider}, with estimated savings of ${formatPhp(recommendation.expected_savings_php)}.`
    : "Ask PadaloAssist when to send money to generate a clear timing recommendation.";

  return (
    <section aria-labelledby="fxpilot-heading" className={className}>
      <Card className="border-[#d6dfdb] shadow-none">
        <CardContent className="flex flex-col gap-4 pt-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex min-w-0 items-start gap-3">
            <span className="flex size-8 shrink-0 items-center justify-center rounded-md bg-[#f8edd1] text-gold">
              <ChartNoAxesCombined className="size-4" aria-hidden="true" />
            </span>
            <div className="min-w-0">
              <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                <h2 id="fxpilot-heading" className="text-sm font-semibold text-ink">
                  FXPilot
                </h2>
                {recommendation ? (
                  <span className="text-xs font-medium text-lagoon">
                    {recommendation.confidence} confidence
                  </span>
                ) : null}
              </div>
              <p className="mt-1 text-sm leading-6 text-muted">{summary}</p>
            </div>
          </div>

          <Dialog>
            <DialogTrigger asChild>
              <Button
                className="shrink-0 self-start sm:self-auto"
                size="sm"
                type="button"
                variant="ghost"
              >
                See more
                <ChevronRight className="size-3.5" aria-hidden="true" />
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl p-5 sm:p-6">
              <DialogHeader>
                <DialogTitle className="text-xl font-semibold text-ink">
                  FXPilot model view
                </DialogTitle>
                <DialogDescription className="text-sm leading-6 text-muted">
                  Historical provider behavior can inform the timing of a remittance. It does not
                  predict a guaranteed rate or fee.
                </DialogDescription>
              </DialogHeader>

              {recommendation ? (
                <dl className="grid gap-4 border-y border-line py-4 sm:grid-cols-3">
                  <div>
                    <dt className="text-xs font-medium text-muted">Recommended day</dt>
                    <dd className="mt-1 text-sm font-semibold text-ink">
                      {recommendation.recommended_day}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs font-medium text-muted">Estimated savings</dt>
                    <dd className="mt-1 text-sm font-semibold text-lagoon">
                      {formatPhp(recommendation.expected_savings_php)}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs font-medium text-muted">Confidence</dt>
                    <dd className="mt-1 text-sm font-semibold text-ink">
                      {recommendation.confidence}
                    </dd>
                  </div>
                </dl>
              ) : (
                <div className="mt-5 flex items-start gap-3 border-y border-line py-4">
                  <Sparkles className="mt-0.5 size-4 shrink-0 text-gold" aria-hidden="true" />
                  <p className="text-sm leading-6 text-muted">
                    Ask PadaloAssist about the best time to send money and FXPilot will return a
                    provider-specific recommendation here.
                  </p>
                </div>
              )}

              <figure className="mt-5 overflow-hidden rounded-md border border-line bg-white">
                <Image
                  alt="FXPilot deterministic backtest comparing Prophet with a naive baseline"
                  className="h-auto w-full"
                  height={720}
                  sizes="(max-width: 672px) calc(100vw - 4rem), 624px"
                  src="/images/fxpilot-backtest.png"
                  width={1280}
                />
                <figcaption className="border-t border-line px-4 py-3 text-xs leading-5 text-muted">
                  Model evaluation on the deterministic synthetic holdout. This visualization is
                  provided for transparency, not as financial advice.
                </figcaption>
              </figure>

              {recommendation ? (
                <p className="mt-4 border-l-2 border-gold pl-3 text-xs leading-5 text-muted">
                  {recommendation.disclaimer}
                </p>
              ) : null}
            </DialogContent>
          </Dialog>
        </CardContent>
      </Card>
    </section>
  );
}
