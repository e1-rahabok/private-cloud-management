# Sources

Source documents for PCM. The author adds them.

| File | What |
|---|---|
| `SP5 Framework.docx` | The SP5 Framework, original. This is the master copy. |
| `sp5-framework.md` and `sp5-framework-media/` | The same document converted to Markdown with pandoc, so AI can search and read it. Regenerate it when the .docx changes. |

Regenerate:

```bash
pandoc "SP5 Framework.docx" -t gfm --wrap=none --extract-media=tmp -o sp5-framework.md
```

Then move `tmp/media/*` to `sp5-framework-media/` and fix the image paths.
