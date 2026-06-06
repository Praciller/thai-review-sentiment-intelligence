---
name: Thai Review Intelligence
description: Calm Thai sentiment analysis for operational review workflows
colors:
  ink-blue: "#0F2D52"
  rice-paper: "#FAF7F1"
  paper-raised: "#FFFDF8"
  tamarind-amber: "#C56A17"
  leaf-green: "#2E7D32"
  clay-red: "#C0392B"
  cool-slate: "#607086"
  divider: "#D8D2C8"
  ink-muted: "#566274"
typography:
  heading:
    fontFamily: "Sarabun, Noto Sans Thai, Segoe UI, sans-serif"
    fontSize: "2rem"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Sarabun, Noto Sans Thai, Segoe UI, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 600
    lineHeight: 1.4
  body:
    fontFamily: "Sarabun, Noto Sans Thai, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Sarabun, Noto Sans Thai, Segoe UI, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
    lineHeight: 1.4
rounded:
  sm: "6px"
  md: "10px"
  lg: "14px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  xxl: "48px"
components:
  button-primary:
    backgroundColor: "{colors.ink-blue}"
    textColor: "{colors.paper-raised}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "12px 20px"
  button-primary-hover:
    backgroundColor: "{colors.tamarind-amber}"
    textColor: "{colors.paper-raised}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "12px 20px"
  input:
    backgroundColor: "{colors.paper-raised}"
    textColor: "{colors.ink-blue}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: "16px"
---

<!-- SEED: re-run impeccable document after implementation to capture final tokens and components. -->

## Overview

**Creative North Star: "The Thai Analyst's Worktable."** The interface should feel
like a well-organized analysis surface used in daylight: warm paper, precise ink,
thin dividers, and data placed where decisions happen.

**The Task-First Rule.** The review input and prediction result dominate the first
viewport. Analytics follows as supporting evidence.

**The Open Surface Rule.** Group with whitespace and dividers. Use cards only when
an element needs a clear interaction boundary.

## Colors

**The Restrained Palette Rule.** Ink blue owns navigation, focus, and primary
actions. Tamarind amber marks the active route and selective emphasis, never large
decorative areas.

Sentiment colors are semantic: leaf green for positive, clay red for negative,
cool slate for neutral and question. Every colored state also includes a text label
or icon.

## Typography

Use one Thai-capable humanist sans family. Sarabun is the preferred web font;
`Noto Sans Thai` and system UI fonts are fallbacks. Product typography uses a fixed
scale. Data values use tabular numerals.

**The Thai-First Measure Rule.** Thai body copy stays at 16px or larger with 1.5
line height. Long explanations are capped near 70 characters per line.

## Elevation

The system is flat by default. Raised surfaces use a paper tint and subtle ambient
shadow only for menus, focused upload zones, or transient feedback.

**The Divider-Before-Shadow Rule.** Try spacing, alignment, and a 1px divider before
adding elevation.

## Components

Buttons, text fields, tabs, filters, probability bars, tables, and charts share the
same 4px spacing rhythm. All controls implement default, hover, focus-visible,
active, disabled, loading, error, and success states where meaningful.

Tables remain tables on wide screens and become labeled row groups on narrow
screens. Loading uses skeleton shapes. Errors appear next to the failed workflow
with a specific recovery action.

## Do's and Don'ts

### Do

- Keep the main review workflow visible without scrolling on desktop.
- Show confidence and all class probabilities.
- Use thin dividers, open bands, and aligned data columns.
- Preserve Thai labels and realistic Thai examples.
- Use motion only for state changes, 150-250ms, with reduced-motion support.

### Don't

- Do not use generic purple-gradient SaaS dashboards.
- Do not use neon, dark-mode machine-learning control rooms.
- Do not use nested cards, bento grids, glass panels, or gradient text.
- Do not encode sentiment by color alone.
- Do not invent model performance numbers.
