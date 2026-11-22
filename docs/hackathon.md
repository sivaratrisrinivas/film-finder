# Hackathon rules brief: Cerebras x Kimi K3.1 Pro x OpenClaw

Source: official "Kimi K3.1 Pro Hackathon" PDF (11 pages, read 2026-11-21) plus docs/handoff.md.

## Hard requirements (miss any one and we're out)
- **Window:** Sat Nov 21, 10:00 AM PT to Sun Nov 22, 10:00 AM PT, which is **Sat 11:30 PM to Sun 11:30 PM IST**. Posts must be published before the deadline.
- **EXTENDED** (Discord @here from organizer InventorBlack, Nov 22): submissions accepted until **Sun Nov 22, 5:00 PM PT = Mon Nov 23, 6:30 AM IST**, because many people couldn't reach the model.
- Kimi K3.1 Pro on Cerebras is a **central component**: model `moonshotai-kimi-k3.1-pro-trial`, standard API, our existing key.
- The project **must use the OpenClaw harness.**
- Core functionality is built during the 24h. Scaffolding, boilerplate and frameworks from before kickoff are allowed.
- **The X post is the official submission.** Tag @Cerebras and @Kimi_Moonshot and include #KimiOnCerebras.
- The post must include: **Project Name, Team Members (X/Reddit handles), Project Description (2–4 sentences), Demo Video (60s max), GitHub repo (recommended, so the repo needs to be public).**
- **Organic engagement only.** No paid promotion, boosting, bots, or engagement farming, or we're disqualified.
- Demo video privacy: no notifications, browser tabs, API keys, emails or credentials visible.

## Prizes
| Prize | Amount | Decided by | Our angle |
|---|---|---|---|
| X Audience Choice | top 3 × $1,000 | organic impressions, counted Tue Nov 24, 10 AM PT | Main target. Hook in the first 3s, visible speed, a public bot link |
| Reddit Audience Choice (r/cerebras) | top 1 × $1,000 | organic upvotes, same tally time; flair "Kimi K3.1 Pro Hackathon" | Same video plus honest eval numbers. Optional but free reach |
| Speed Bounty: "Santa's Speedy Shopper" | 1 × $1,000 | highest TPS | **Separate task**: OpenClaw + Kimi finds 5 real Christmas gifts with real product links. Needs the official OpenClaw speed patch (from organizers; don't share it, don't use it in public demos). Enter by posting a video in Discord #share-your-demo with the TPS in the message text. **Undecided whether we do this.** |

One project can win all three.

## Video guidance (from the PDF)
- 60s max. Clearly show how Cerebras speed improves the experience.
- Recommended: a side-by-side with a GPU provider.
- Focus on key features, workflow, impact.

## Limits and access
- 100 RPM and 100K TPM per participant. Cached tokens don't count. Prompt caching is supported.
- Access lasts until Mon Nov 23, 10 AM PT.
- **Reasoning:** the PDF says "thinking is off by default; set `reasoning_effort`". Our live test disagrees: with `reasoning_effort` unset, "Say OK." still used 36 reasoning tokens. Trust the measurement and set `reasoning_effort` explicitly on every call.

## Support
- Discord, Kimi K3.1 Pro Hackathon category: #announcements, #hackathon-chat, #hackathon-support, #share-your-demo.
- Live engineer hours: **Sat 10:30 AM–12:30 PM PT (Sun 12:00–2:00 AM IST)** and **Sun 9–10 AM PT (Sun 10:30–11:30 PM IST)**. Limited help overnight PT, so ask early.

## Ask an organizer (during live hours)
1. Is using a GPU provider only for the side-by-side clip fine, as long as the bot runs only on Kimi/Cerebras? (The PDF recommends it, so probably yes.)
2. Reasoning default: the docs say off, but we see reasoning tokens with it unset. Which is right?
