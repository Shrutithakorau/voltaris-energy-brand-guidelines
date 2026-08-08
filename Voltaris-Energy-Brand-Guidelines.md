# Voltaris Energy — Brand Guidelines

**Version:** 1.0  
**Source:** Derived from [voltarisenergy.com.au](https://www.voltarisenergy.com.au) (August 2026)  
**Purpose:** Keep all Voltaris Energy marketing, web, and sales materials visually and verbally consistent.

---

## 1. Brand overview

### Who we are

Voltaris Energy is an **Australian-owned**, **CEC-accredited** solar and battery installer. We design and install premium home and commercial solar battery systems for Australian families and businesses — with honest local support from consultation through ongoing aftercare.

### Mission

Help Australians cut rising power costs, store solar energy, gain backup protection during outages, and enjoy lasting daily savings through intelligent energy systems.

### Positioning

Premium, trustworthy, and practical — not hype-driven. We emphasise **expertise, Tier-1 hardware, rebate guidance, and end-to-end project management**.

### Tagline / primary headline idea

> **Power Your Home with Intelligent Energy**

Alternate / supporting lines:

- Power your property with intelligent solar
- Powering Australian Homes with Smarter Energy Storage
- Take Control of Your Energy Bills

---

## 2. Brand personality

| Trait | How it shows up |
| --- | --- |
| **Trustworthy** | CEC accreditation, warranties, clear process, no-pressure consultation |
| **Local & Australian** | Australian-owned, Melbourne home base, Australia-wide coverage |
| **Intelligent** | Tailored systems, usage-based design, savings estimates |
| **Premium but accessible** | Tier-1 brands + clear pricing / rebate / finance pathways |
| **Reassuring** | Backup power, ongoing support, "we handle everything" |

**Tone of voice:** Confident, clear, and helpful. Speak to homeowners and business owners in plain English. Prefer benefits and outcomes (lower bills, backup, independence) over jargon. Be specific where possible (system sizes, warranties, timelines). Avoid aggressive sales language and empty buzzwords.

---

## 3. Logo & brand mark

### Current usage (web)

- Logo appears in the fixed pill navigation as a horizontal wordmark/image (`nav-logo`).
- Recommended display height in primary nav: **~44px**.
- Clear space: keep at least the height of the mark's "V" around all sides when possible.
- On light UI, place the logo on **white** or **cream** backgrounds.

### Do

- Use the official logo files only (SVG preferred for digital).
- Maintain aspect ratio; never stretch or skew.
- Use on high-contrast backgrounds (white, cream, or deep navy).

### Don't

- Recolour the logo arbitrarily (except approved mono/reverse versions if provided).
- Place on busy photography without a scrim or solid backing.
- Add drop shadows, outlines, or glow effects to the mark.
- Pair with unofficial taglines that compete with the wordmark.

### Favicon / app icons

Site assets include:

- `/favicon.svg`
- `/favicon-32x32.png`
- `/favicon-16x16.png`
- `/favicon.ico`

Use the SVG favicon for web where supported.

---

## 4. Colour palette

Colours below are taken from the live site CSS tokens (`:root` in `home.css` / `site-chrome.css`).

### Primary brand colours

| Token | Hex | Role |
| --- | --- | --- |
| **CTA Yellow** `--cta` | `#FFC70A` | Primary buttons, key accents, progress bars |
| **CTA Hover** `--cta-hover` | `#F0BB00` | Button hover / pressed |
| **CTA Text** `--cta-text` | `#090909` | Text on yellow CTAs |
| **Near Black** | `#090909` | High-contrast text / CTA label |
| **Dark** `--dark` | `#1A1E1B` | Primary body text, nav text |
| **Dark 2** `--dark-2` | `#232820` | Secondary dark surfaces |
| **White** `--white` | `#FFFFFF` | Page background, cards, nav |

### Supporting / accent colours

| Token | Hex | Role |
| --- | --- | --- |
| **Lime** `--lime` | `#D4E84A` | Fresh energy accent (sparingly) |
| **Lime Mid** `--lime-mid` | `#C8DC30` | Secondary lime accent |
| **Lime Pale** `--lime-pale` | `#F5FAD0` | Soft highlight backgrounds |
| **Navy** | `#11234B` / `#102445` | Hero / section gradients, depth |
| **Deep Navy** | `#0D1A3A` | Darker navy variant |
| **Teal** | `#0F766E` | Occasional trust / eco accent |

### Neutrals & surfaces

| Token | Hex | Role |
| --- | --- | --- |
| **Cream** `--cream` | `#F7F5EE` | Soft section backgrounds |
| **Cream Warm** `--cream-warm` | `#EFEDE6` | Alternate warm surface |
| **Mid** `--mid` | `#4A4F46` | Secondary text |
| **Muted** `--muted` | `#757870` | Supporting / caption text |
| **Slate** | `#596475` | UI secondary copy |
| **Border** `--border` | `#E2DDD4` | Dividers, nav border |
| **Border Mid** `--border-mid` | `#C8C3B8` | Stronger borders |
| **Grey 500** | `#6B7280` | Form / helper text |
| **Grey 200** | `#E5E7EB` | Light UI borders |
| **Soft Grey BG** | `#F5F6F8` / `#F9FAFB` | Subtle panels |

### Colour usage rules

1. **Yellow (`#FFC70A`) is the action colour** — reserve for CTAs ("Get a free quote", "Call...") and critical highlights.
2. **CTA text on yellow is always near-black (`#090909`)**, never white.
3. Body text defaults to **`#1A1E1B`** on white/cream.
4. Use **navy gradients** for hero depth and premium sections — not purple or generic tech gradients.
5. Lime accents are optional emphasis only; do not replace CTA yellow.
6. Maintain WCAG AA contrast for text (especially muted greys on cream).

### Example CTA treatment

```css
background: #FFC70A;
color: #090909;
/* hover */
background: #F0BB00;
box-shadow: 0 8px 24px rgba(255, 199, 10, 0.45);
```

---

## 5. Typography

### Primary type system (site tokens)

| Role | Family | CSS token / notes |
| --- | --- | --- |
| **Display / headlines (serif)** | **DM Serif Display** | `--font-serif` — expressive section titles |
| **UI / body (sans)** | **DM Sans** | `--font-sans` — nav, body, buttons |
| **Marketing sans (alternate)** | **Plus Jakarta Sans** | Used across marketing UI blocks |
| **Supporting UI** | **Inter** | Utility / secondary UI in places |
| **Compact display** | **Space Grotesk** | Occasional label / compact headings |

### Recommended hierarchy (digital)

| Level | Style |
| --- | --- |
| **H1** | DM Serif Display, ~40–56px, weight 400, tight tracking, dark `#1A1E1B` |
| **H2** | DM Serif Display or Plus Jakarta Sans Bold, ~32–40px |
| **H3 / card titles** | Plus Jakarta Sans / DM Sans Semibold–Bold, ~20–24px |
| **Body** | DM Sans Regular 16px / line-height ~1.6 |
| **Nav / labels** | DM Sans Medium 14px |
| **CTA buttons** | DM Sans Bold 14px |
| **Captions / helper** | DM Sans 13–14px, muted `#757870` or `#596475` |

### Google Fonts import (reference)

```
DM Sans (400–700)
DM Serif Display (regular + italic as needed)
Plus Jakarta Sans (as used on site)
```

### Typography rules

- Prefer sentence case for UI; avoid ALL CAPS except short labels (e.g. section eyebrows).
- Keep headlines benefit-led and scannable (one idea per heading).
- Do not mix more than two primary families in a single composition (serif display + sans body is the core pairing).
- Australian English spelling: *customise, organised, colour, metre (where appropriate), licence (noun)*.

---

## 6. Imagery & iconography

### Photography themes

- Australian homes with visible solar / battery installs
- Clean rooftop panels, hybrid inverters, wall-mounted batteries
- Real suburban / coastal Victoria feel (Mornington, Rosebud–style lifestyle contexts)
- Bright, natural daylight; avoid heavy filters and neon overlays

Hero image references on site include:

- Solar + battery product photography
- Installed-home lifestyle shots
- Soft estimator / CTA backgrounds

### Icon style

- Custom SVG icons (line/simple filled), consistent stroke weight
- Trust badges: CEC, Australian-owned, rebate assistance, premium batteries
- Benefit icons for bill savings, backup, independence, grid reduction, future-proofing
- Map pins for service areas

### Partner / hardware brands (logo strip)

Use official partner marks only, with correct clear space and mono/colour rules from each brand:

- Sungrow
- Tesla
- AlphaESS
- Sigenergy
- GoodWe
- Fox Ess (featured in package copy)

Never alter partner logos or present Voltaris as the manufacturer of those brands.

---

## 7. UI & layout patterns

### Signature UI behaviours (from site)

- **Floating pill navigation** — white, rounded (`border-radius: 100px`), subtle border `#E2DDD4`, soft shadow
- **Pill CTAs** — yellow fill, fully rounded, bold dark label
- **Soft cards / panels** — cream or white surfaces; avoid heavy multi-shadow stacks
- **Motion** — restrained: fade-up on scroll, gentle float on decorative elements; purposeful, not noisy
- **Max content width** — ~1180px for primary chrome

### Corner radius guidance

| Element | Radius |
| --- | --- |
| Nav / primary CTA | Fully rounded (pill) |
| Dropdowns | ~18px |
| Menu links / small controls | ~12px |
| Large media | Soft, consistent — avoid random radii |

### Spacing

Use generous section padding and clear hierarchy: eyebrow → headline → one supporting sentence → primary action. One job per section.

---

## 8. Messaging framework

### Audience

1. **Residential** — families wanting lower bills, backup power, and rebate-assisted solar + battery
2. **Commercial** — businesses seeking ROI, STCs/LGCs, sustainability credentials, and minimal install disruption

### Key messages (residential)

- Cut rising power costs with premium solar battery installation
- Store solar energy and stay protected during outages
- Tailored systems for your household's usage patterns
- Government rebate assistance and interest-free finance options
- CEC-accredited installers; premium Tier-1 batteries

### Key messages (commercial)

- Reduce operating costs and strengthen sustainability credentials
- Custom design for rooftops, ground mounts, storage, EV charging, monitoring
- In-house licensed installers; strong warranties
- Typical payback framing: often within ~3–7 years (context-dependent)

### Proof points to reuse

- CEC Accredited Installers
- Australian-Owned
- Government Rebate Assistance
- Premium / Tier-1 Battery & Panel Brands
- End-to-end project management + ongoing support
- Installation timing: often **1–2 days** residential; **2–5 days** commercial (site-dependent)
- Battery warranties commonly **10–15 years** (brand-dependent)

### Example package language (site)

- **Combo 01 · Family Saver** — 10.3kW Solar + 20kWh Battery — from **$7,000** (as advertised; confirm live pricing)
- **Combo 02 · Best Value** — 13.3kW Solar + 25kWh Battery — from **$8,000** (as advertised; confirm live pricing)

Always verify current pricing, inclusions, and rebate assumptions before publishing.

### CTAs (preferred)

- Get a free quote
- Get Free Quote
- Call 0430 741 441
- Request Commercial Consultation
- Check Your Rebate Eligibility

### Words to favour

intelligent energy · premium · tailored · accredited · backup · savings · rebate · Australian-owned · Tier-1 · end-to-end · no obligation

### Words / tones to avoid

cheap / cheapest · hard sell · scare tactics · unverifiable "#1" claims · greenwashing without substance · US spelling in AU materials

---

## 9. Contact & legal (for materials)

| Item | Value |
| --- | --- |
| **Website** | https://www.voltarisenergy.com.au |
| **Phone** | 0430 741 441 |
| **Privacy** | Reference Privacy Policy on voltarisenergy.com.au |
| **Marketing consent** | Align with site consent copy (VEU / energy-efficient products where applicable); always include opt-out language |

When collecting leads, state that details stay private and that the team typically responds within **24 hours** (as per site).

---

## 10. Service geography

Lead with **Melbourne** as home base; support national messaging for:

Melbourne · Sydney · Brisbane · Adelaide · Perth · (Commercial also lists Canberra)

---

## 11. Application checklist

Before publishing any asset, confirm:

- [ ] Logo is correct file, unstretched, with clear space
- [ ] Primary CTA uses `#FFC70A` with `#090909` text
- [ ] Headlines use approved serif/sans pairing
- [ ] Spelling is Australian English
- [ ] Claims match current offers, warranties, and rebate rules
- [ ] Partner brand logos follow their guidelines
- [ ] Contact phone / URL are correct
- [ ] Contrast is readable on cream and navy backgrounds

---

## 12. Quick reference card

```
Brand:     Voltaris Energy
Promise:   Intelligent solar & battery for Australian homes & businesses
CTA:       #FFC70A  text #090909
Text:      #1A1E1B
Surface:   #FFFFFF / #F7F5EE
Accent:    Navy #11234B · Lime #D4E84A
Fonts:     DM Serif Display (display) + DM Sans (UI/body)
CTA copy:  Get a free quote  |  0430 741 441
```

---

*This document is a working brand guideline synthesised from the public Voltaris Energy website design system and messaging. Update tokens, pricing, and claims whenever the live site or brand assets change.*
