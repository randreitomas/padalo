import Link from "next/link";
import { ArrowRight, Bot, Database, Network, ShieldCheck, WalletCards } from "lucide-react";

import { MacDashboardPreview } from "@/components/marketing/mac-dashboard-preview";
import { Button } from "@/components/ui/button";

const storyRows = [
  {
    number: "01",
    title: "The problem",
    headline: "A remittance arrives. The context often does not.",
    description:
      "Families coordinate needs, due dates, and decisions across distance. A transfer confirms what was sent, but not what the household can safely plan next.",
  },
  {
    number: "02",
    title: "The solution",
    headline: "One calm picture for everyone involved.",
    description:
      "Padalo keeps envelopes, commitments, and recent activity in one shared view. The record stays clear without asking anyone to justify every decision.",
  },
  {
    number: "03",
    title: "The product",
    headline: "A practical assistant for the next conversation.",
    description:
      "Ask about tuition, a due date, or the right day to send. Padalo returns grounded household context in language people can use together.",
  },
];

const steps = [
  {
    number: "01",
    title: "Keep the household picture current",
    description: "Record remittances, envelopes, bills, and everyday spending in one shared place.",
  },
  {
    number: "02",
    title: "Ask a practical question",
    description:
      "PadaloAssist checks the relevant balances, recent activity, and commitments before it responds.",
  },
  {
    number: "03",
    title: "Decide with more context",
    description:
      "Bring a clear recommendation back to the family conversation and plan the next move together.",
  },
];

const architecture = [
  { icon: WalletCards, title: "Shared ledger", description: "Budgets, bills, and remittances" },
  {
    icon: Bot,
    title: "Typed agent tools",
    description: "Useful context without direct database access",
  },
  {
    icon: Network,
    title: "Streaming responses",
    description: "Visible progress while a question is checked",
  },
  { icon: Database, title: "Neon PostgreSQL", description: "A durable household record" },
  { icon: ShieldCheck, title: "Trust-sensitive UX", description: "Clear language, careful limits" },
];

export function LandingPage() {
  return (
    <div className="overflow-x-hidden bg-[#f7f8f7] text-[#17201d]">
      <main id="main-content">
        <section aria-labelledby="hero-title" className="border-b border-[#dce3df]">
          <div className="mx-auto max-w-[1160px] px-5 pb-14 pt-16 sm:px-8 sm:pb-20 sm:pt-20 lg:px-0 lg:pb-24 lg:pt-24">
            <div className="mx-auto max-w-[820px] text-center">
              <h1
                id="hero-title"
                className="landing-reveal landing-reveal-delay-1 text-5xl font-extrabold leading-[1.02] tracking-tight sm:text-6xl lg:text-[82px]"
              >
                Send with care.
                <br />
                <span className="text-lagoon">Plan with clarity.</span>
              </h1>
              <p className="landing-reveal landing-reveal-delay-2 mx-auto mt-6 max-w-[620px] text-base leading-7 text-[#586660] sm:text-lg sm:leading-8">
                AI-powered remittance intelligence for OFW families. Padalo turns household budgets,
                bills, and timing into a calmer next conversation.
              </p>
              <div className="landing-reveal landing-reveal-delay-3 mt-8 flex flex-wrap justify-center gap-3">
                <Button
                  asChild
                  className="h-11 rounded-full px-6 hover:-translate-y-px motion-reduce:hover:translate-y-0"
                >
                  <Link href="/dashboard">
                    Start demo
                    <ArrowRight aria-hidden="true" className="size-4" />
                  </Link>
                </Button>
                <Button
                  asChild
                  className="h-11 rounded-full px-6 hover:-translate-y-px motion-reduce:hover:translate-y-0"
                  variant="secondary"
                >
                  <a href="#architecture">View architecture</a>
                </Button>
              </div>
            </div>

            <MacDashboardPreview
              className="landing-reveal landing-reveal-delay-3 mx-auto mt-12 max-w-[1080px] sm:mt-16"
              variant="hero"
            />
          </div>
        </section>

        <section aria-labelledby="story-title" className="bg-white">
          <div className="mx-auto max-w-[1160px] px-5 py-20 sm:px-8 lg:px-0 lg:py-28">
            <div className="max-w-[650px]">
              <p className="text-sm font-bold tracking-[0.12em] text-lagoon">THE HOUSEHOLD STORY</p>
              <h2
                id="story-title"
                className="mt-4 text-4xl font-bold leading-[1.08] tracking-tight sm:text-5xl"
              >
                Better decisions begin with a shared picture.
              </h2>
            </div>

            <ol className="mt-12 border-t border-[#dce3df]">
              {storyRows.map((row) => (
                <li
                  key={row.number}
                  className="grid gap-5 border-b border-[#dce3df] py-9 sm:py-11 lg:grid-cols-[7rem_minmax(0,1fr)_minmax(0,0.8fr)] lg:gap-8"
                >
                  <p className="text-3xl font-extrabold tracking-tight text-lagoon tabular-nums">
                    {row.number}
                  </p>
                  <div>
                    <p className="text-sm font-bold tracking-[0.1em] text-[#53625c]">{row.title}</p>
                    <h3 className="mt-3 max-w-[620px] text-2xl font-bold leading-[1.12] tracking-tight text-[#1b2924] sm:text-3xl">
                      {row.headline}
                    </h3>
                  </div>
                  <p className="max-w-[430px] text-sm leading-7 text-[#62716a] sm:text-base">
                    {row.description}
                  </p>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section
          id="product"
          aria-labelledby="product-title"
          className="border-y border-[#dce3df] bg-[#f3f6f4]"
        >
          <div className="mx-auto max-w-[1160px] px-5 py-20 sm:px-8 lg:px-0 lg:py-28">
            <div>
              <p className="text-sm font-bold tracking-[0.12em] text-lagoon">THE PRODUCT</p>
              <h2
                id="product-title"
                className="mt-4 max-w-none text-4xl font-bold leading-[1.04] tracking-tight sm:text-5xl lg:text-[64px]"
              >
                A clearer household view, before anyone needs to ask twice.
              </h2>
            </div>

            <div className="mt-10 grid gap-4 lg:grid-cols-3">
              <article className="min-h-[410px] overflow-hidden rounded-lg border border-[#dce3df] bg-white p-5 lg:col-span-2 sm:p-7">
                <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-start">
                  <div>
                    <p className="text-sm font-bold text-[#1c3029]">Household overview</p>
                    <p className="mt-2 max-w-[430px] text-sm leading-6 text-[#64716c]">
                      The essentials stay visible in one quiet, legible view.
                    </p>
                  </div>
                  <span className="inline-flex w-fit rounded-full bg-[#e7f3ef] px-3 py-1 text-xs font-bold text-lagoon">
                    Shared by design
                  </span>
                </div>
                <MacDashboardPreview className="mt-6 h-[275px] sm:h-[290px]" variant="overview" />
              </article>

              <article
                id="intelligence"
                className="min-h-[410px] overflow-hidden rounded-lg border border-[#dce3df] bg-white p-5 sm:p-7"
              >
                <p className="text-sm font-bold text-[#1c3029]">PadaloAssist</p>
                <p className="mt-2 text-sm leading-6 text-[#64716c]">
                  A practical answer, with the household context behind it.
                </p>
                <MacDashboardPreview className="mt-6 h-[275px]" variant="assist" />
              </article>

              <article
                id="fxpilot"
                className="min-h-[410px] overflow-hidden rounded-lg border border-[#dce3df] bg-white p-5 sm:p-7"
              >
                <p className="text-sm font-bold text-[#1c3029]">FXPilot</p>
                <p className="mt-2 text-sm leading-6 text-[#64716c]">
                  A timing signal based on provider behavior, never a promise.
                </p>
                <MacDashboardPreview className="mt-6 h-[275px]" variant="fxpilot" />
              </article>

              <article className="flex min-h-[410px] flex-col overflow-hidden rounded-lg border border-[#dce3df] bg-white p-5 lg:col-span-2 sm:p-7">
                <p className="text-sm font-bold text-[#1c3029]">
                  One place to prepare the next move
                </p>
                <p className="mt-2 max-w-[620px] text-sm leading-6 text-[#64716c]">
                  What arrived, what is committed, and what is still available can sit beside the
                  question a family actually needs to answer.
                </p>
                <dl className="mt-6 grid min-h-0 flex-1 grid-rows-3 gap-3">
                  <div className="flex min-h-0 items-center justify-between gap-5 rounded-md bg-[#e7f3ef] px-4 py-4 sm:px-5">
                    <dt className="text-sm font-bold text-[#176554] sm:text-base">Available now</dt>
                    <dd className="text-2xl font-extrabold tracking-tight text-[#176554] tabular-nums sm:text-3xl">
                      P24,381
                    </dd>
                  </div>
                  <div className="flex min-h-0 items-center justify-between gap-5 rounded-md bg-[#fcf3da] px-4 py-4 sm:px-5">
                    <dt className="text-sm font-bold text-[#8a6200] sm:text-base">Visible ahead</dt>
                    <dd className="text-2xl font-extrabold tracking-tight text-[#8a6200] tabular-nums sm:text-3xl">
                      4 bills
                    </dd>
                  </div>
                  <div className="flex min-h-0 items-center justify-between gap-5 rounded-md bg-[#e8eff8] px-4 py-4 sm:px-5">
                    <dt className="text-sm font-bold text-[#376d93] sm:text-base">
                      FXPilot signal
                    </dt>
                    <dd className="text-2xl font-extrabold tracking-tight text-[#376d93] tabular-nums sm:text-3xl">
                      Thursday
                    </dd>
                  </div>
                </dl>
              </article>
            </div>
          </div>
        </section>

        <section id="workflow" aria-labelledby="workflow-title" className="bg-white">
          <div className="mx-auto max-w-[1160px] px-5 py-20 sm:px-8 lg:px-0 lg:py-28">
            <div className="mx-auto max-w-[710px] text-center">
              <p className="text-sm font-bold tracking-[0.12em] text-lagoon">HOW IT WORKS</p>
              <h2
                id="workflow-title"
                className="mt-4 text-4xl font-bold leading-[1.08] tracking-tight sm:text-5xl"
              >
                A calmer route to the next decision.
              </h2>
            </div>

            <ol className="mt-12 grid gap-4 md:grid-cols-3">
              {steps.map((step) => (
                <li
                  key={step.number}
                  className="rounded-lg border border-[#dce3df] bg-[#fbfcfb] p-6 sm:p-7"
                >
                  <span className="inline-flex size-9 items-center justify-center rounded-full bg-[#e7f3ef] text-sm font-extrabold text-lagoon">
                    {step.number}
                  </span>
                  <h3 className="mt-8 text-xl font-bold leading-tight tracking-tight text-[#1d3029]">
                    {step.title}
                  </h3>
                  <p className="mt-3 text-sm leading-7 text-[#65736d]">{step.description}</p>
                </li>
              ))}
            </ol>
          </div>
        </section>

        <section
          id="architecture"
          aria-labelledby="architecture-title"
          className="border-y border-[#dce3df] bg-[#eef3f0]"
        >
          <div className="mx-auto max-w-[1160px] px-5 py-20 sm:px-8 lg:px-0 lg:py-24">
            <div className="max-w-[620px]">
              <p className="text-sm font-bold tracking-[0.12em] text-lagoon">ARCHITECTURE</p>
              <h2
                id="architecture-title"
                className="mt-4 text-3xl font-bold leading-[1.1] tracking-tight sm:text-4xl"
              >
                A focused system behind every answer.
              </h2>
            </div>
            <ol className="mt-10 grid gap-0 border-y border-[#d6e0db] sm:grid-cols-2 lg:grid-cols-5 lg:border-b-0">
              {architecture.map((item) => {
                const Icon = item.icon;

                return (
                  <li
                    key={item.title}
                    className="border-b border-[#d6e0db] px-5 py-6 lg:border-b-0 lg:border-r lg:last:border-r-0"
                  >
                    <Icon className="size-4 text-lagoon" aria-hidden="true" />
                    <p className="mt-5 text-sm font-bold text-[#1c3029]">{item.title}</p>
                    <p className="mt-2 text-sm leading-6 text-[#66746e]">{item.description}</p>
                  </li>
                );
              })}
            </ol>
          </div>
        </section>

        <section aria-labelledby="final-cta-title" className="bg-[#182b25] text-white">
          <div className="mx-auto max-w-[1160px] px-5 py-20 text-center sm:px-8 lg:px-0 lg:py-24">
            <p className="text-sm font-bold tracking-[0.12em] text-[#c8e4dc]">PADALO</p>
            <h2
              id="final-cta-title"
              className="mt-5 text-4xl font-bold leading-[1.08] tracking-tight sm:text-5xl"
            >
              A clearer way to send care home.
            </h2>
            <p className="mx-auto mt-5 max-w-[530px] text-base leading-7 text-[#d0ddd8] sm:text-lg">
              Open the Santos Family demo and see what a shared household picture can make easier.
            </p>
            <Button
              asChild
              className="mt-8 h-11 rounded-full bg-white px-6 text-[#176f68] hover:-translate-y-px hover:bg-[#e7f0ed] motion-reduce:hover:translate-y-0"
            >
              <Link href="/dashboard">
                Start the demo
                <ArrowRight aria-hidden="true" className="size-4" />
              </Link>
            </Button>
          </div>
        </section>
      </main>

      <footer className="bg-[#101b17] text-[#c9d4d0]">
        <div className="mx-auto max-w-[920px] px-5 py-8 text-center text-xs leading-6 sm:px-8 sm:text-sm">
          <p>
            Built with OpenAI <span aria-hidden="true">·</span> GPT-5.6 Terra Ultra{" "}
            <span aria-hidden="true">·</span> OpenAI Build Week 2026{" "}
            <span aria-hidden="true">·</span> Developed by Ralph Andrei Masangkay{" "}
            <span aria-hidden="true">·</span>{" "}
            <a
              className="font-semibold text-white transition-colors hover:text-[#bfe3d9]"
              href="https://www.linkedin.com/in/randreitomas"
              rel="noreferrer"
              target="_blank"
            >
              LinkedIn
            </a>{" "}
            <span aria-hidden="true">·</span>{" "}
            <a
              className="font-semibold text-white transition-colors hover:text-[#bfe3d9]"
              href="https://github.com/randreitomas"
              rel="noreferrer"
              target="_blank"
            >
              GitHub
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
}
