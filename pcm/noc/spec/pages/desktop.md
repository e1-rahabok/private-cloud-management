---
page: /noc
question: "What does the wall show, and where exactly?"
role: l1
cadence: [live]
vocabulary: pcm/noc/spec/vocabulary.yaml
design: pcm/noc/design-note.md
decisions: [D-032, D-041, D-052, D-098]
---

# NOC desktop: the five screens with drill-down

## The five screens

```yaml
question: "What does the wall show, and where exactly?"
role: l1
cadence: [live]
reads: [noc.screen_status]
api: /api/noc/wall
```

- **The same data and colours as the wall** (NOC design, 3.3), shown as six tabs, named as on the wall (D-107). There is no rotation.
- **A tile in Performance opens the cluster:**
  - top villains and victims, with their scores from 0 to 100;
  - their environment: production or non-production;
  - their class.
- **A red or amber tile links to its incident** on `/noc/alert/{id}`.
- **A navigation bar links** to Alerts and Shift. It does not link to other workspaces (D-011). The Agent E2 mark sits at its right (below).
- **Agent E2 mark** on each tile, "Ask Agent E2 about {tile}", and on the cluster drill-down, "Ask Agent E2 about {cluster}".
  - Suggestions, tile: "What does this tile tell me?", "What does the SOP say I should do?".
  - Suggestions, cluster: "Why is this cluster not serving its VMs well?", "Who is the villain, and is it production?", "What does the SOP say I should do?".
  - Suggestions, the page (top bar mark): "What needs me first?", "Explain this screen in plain words."
  - PCM sends: the screen and its tiles (names, statuses, counts); for a tile, that tile; for a cluster, its score now and an hour ago, villains and victims with class, environment and score.
- **States:**
  - normal;
  - stale;
  - empty: "Nothing to show";
  - loading;
  - error.

## Agent E2 mark and panel

```yaml
question: "Can Agent E2 explain what I am looking at, in my words?"
role: l1
cadence: [live]
api: /api/noc/agent/ask
decisions: [D-097, D-098]
```

- **The mark and the panel are L2's** (L2 frame, Agent E2 mark and Agent E2 panel): "E2" in a rounded square; the panel docks on the right, 400 px, and pushes the page; Esc closes it; one conversation per context for the browser session.
- **In the top bar,** right of the navigation, before the time: dark with a green dot when the service answers, grey when not. A click asks about the page.
- **PCM sends L1's facts with the role l1:** scores from 0 to 100, the SOP and its results, never a raw counter. The words of every answer are checked against the NOC vocabulary (NOC design, 3.8; D-098):
  - an answer with an avoided word is asked for once more, naming the words;
  - if it fails again: "Agent E2's answer used words that are not used on this screen. Escalate if you need the detail." and no answer.
- **No action button in the panel.** Agent E2 does not acknowledge, act, escalate or close.
- **Not available:** the mark is grey and the panel says "The Agent E2 service is not available." When the service answers but its model does not: "Agent E2 is running, but its model cannot be reached."
