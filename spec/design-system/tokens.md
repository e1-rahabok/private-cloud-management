# Design tokens

Taken from the Executive Dashboard mockup (D-015), which is already accessible. Tokens live in one theme file in the build. Workspaces share tokens and components but no menu (D-011).

## Colour roles

| Token | Value | Use |
|---|---|---|
| `page.bg` | `#EFEDE6` | Warm light page background |
| `page.bg.alt` | `#F3F1EC` | Alternate band |
| `hero.bg` | `#0B1B2B` | Dark navy hero |
| `hero.bg.raised` | `#12202E` | Raised surface on the hero |
| `card.bg` | `#FFFFFF` | Cards |
| `line` | `#E4E2DA` | Borders and dividers |
| `text` | `#0B1B2B` | Body text on light |
| `text.muted` | `#5B6877` | Secondary text on light |
| `text.on-dark.muted` | `#A9BACB` | Secondary text on the hero |
| `accent` | `#0E9F8E` | Healthy, in use, the single accent |
| `accent.strong` | `#0A7A6D` | Accent text on white (5.2:1) |
| `accent.ink` | `#0A5E54` | Accent text on `accent.soft` (6.2:1). The mockup used `accent.strong` here, which is 4.2:1, below 4.5:1 (found by page test PG-9). |
| `accent.soft` | `#D2ECE5` | Accent chip background |
| `accent.on-dark` | `#5EEAD4` | Accent on the hero |
| `amber` | `#B45309` | Watch: text and lines |
| `amber.soft` | `#F5E1B8` | Watch chip background |
| `amber.ink` | `#7A3B06` | Watch chip text on `amber.soft` (6.7:1). `amber` on `amber.soft` is 3.9:1, below 4.5:1. |
| `red` | `#8F1D13` | Act now: text and lines |
| `red.soft` | `#F6D6D1` | Act-now chip background |
| `focus` | `#2F6FDE` | Focus ring |
| `stale` | `#B8C2CC` | Grey for "No data" (D-041) |
| `waste` | `#3E5C79` | Dark grey for waste (Capacity design, 3.3). Not used on the Executive page. |

## Status chips

| Status | Background | Text | Label (Executive) |
|---|---|---|---|
| `green` | `accent.soft` | `accent.ink` | Good |
| `amber` | `amber.soft` | `amber.ink` | Watch |
| `red` | `red.soft` | `red` | Act now |
| `in_plan` | `accent.soft` | `accent.ink` | In the plan |
| `no_data` | `#E7E5DD` | `text.muted` | No data |

- **Colour is never the only signal.** Every colour comes with a text label (mockup rule, WCAG).
- `in_plan` uses the accent, not amber. A short date already covered by the next purchase round is not an alarm (Executive design, 4.4).

## Type

- Typeface: Manrope, with system-ui as fallback.
- Numbers use tabular figures.

## Graphics

- Custom SVG only. No emoji, no stock icon packs (mockup rule).
- Chart reference lines: a dashed amber line for targets.
- Reduced motion is respected: animations stop when the user asks for reduced motion.

## Accessibility

- Text contrast at least 4.5:1.
- All controls work by keyboard. Expanding buttons use `aria-expanded`; towers use `aria-pressed` (mockup rule).
