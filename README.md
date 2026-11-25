# FansCut Community

The list of fan cuts that [FansCut](https://github.com/jhd3197/FansCut) shows on
**Discover**. FansCut reads [`index.json`](index.json) and checks every entry
against the viewer's own library, so it can say "Ready", "Missing Episode IX",
or offer an install.

This repo is only the list. Each cut lives in its own repo with its recipe,
`fanscut.json`. A recipe holds timestamps, ordering and fingerprints that
re-time the cuts to the viewer's own copies. **Nothing here, and nothing in a
cut repo, contains video, audio, subtitles or artwork.** Viewers need their own
copies of the films or episodes.

## Cuts in the index

> This table mirrors [`index.json`](index.json). FansCut reads the JSON; if the
> two disagree, the JSON is right.

| Cut | Kind | Needs |
|---|---|---|
| _None yet._ | | |

## How FansCut uses it

- FansCut fetches
  `https://raw.githubusercontent.com/jhd3197/fanscut-community/main/index.json`
  (setting `community.index_url`) and keeps it for 10 minutes. If the fetch
  fails, it keeps showing the last list it had.
- Listing is read-only. A cut is installed only when someone presses
  **Install**: FansCut then reads `fanscut.json` from the cut's repo at its
  latest commit, and offers updates when that repo moves on.
- `community.index_url` can point at another index, such as a fork or a local
  `index.json`, to try out entries before they're published.

## Adding a cut

1. Put the cut in its own **public** GitHub repo, with these at the root:
   - `fanscut.json`: the recipe. Make it in FansCut (New cut from template, the
     editor, then Export). Run `fanscut recipe validate --file fanscut.json`.
   - `README.md`: what the cut is, which editions it was timed against, credits.
   - `outline.md` (optional): the scene list, in plain words.
2. Open a pull request here that adds one entry to `cuts` in `index.json` and a
   row to the table above.
3. CI runs `scripts/validate.py --online`. It checks the entry and that the
   repo is public with a `fanscut.json`. A private repo can't be listed:
   FansCut installs cuts without a GitHub token.

### An entry

```json
{
  "name": "Short name shown on the tile",
  "repo": "https://github.com/<owner>/<repo>",
  "kind": "merge",
  "category": "Fantasy",
  "tagline": "One line, up to 80 characters",
  "sources": [
    {"tmdb": 49051, "title": "The Hobbit: An Unexpected Journey", "edition": "Extended"},
    {"tmdb": 120, "title": "The Fellowship of the Ring", "edition": "Extended", "optional": true}
  ],
  "variants": ["Book cut"]
}
```

- `kind`: `merge`, `supercut`, `order`, `canon`, `character`, `chronological` or `cut`.
- `sources`: what a viewer must own. Films use `tmdb`, shows use `tvdb`
  (plus `episodes` for how many it uses). Mark a source `optional` when only
  some variants need it.
- `category`: the Discover shelf the cut goes on.
- `poster` (optional): an https image.

The full rules are in [`schema/index.schema.json`](schema/index.schema.json).

```bash
python scripts/validate.py            # the shape
python scripts/validate.py --online   # plus: every repo is public with a recipe
```

## Rules

- One franchise per cut. A cut stays inside one series or film collection.
- No media, ever: no video, audio, subtitles, thumbnails, logos or fonts, in
  this repo or in a cut's repo.
- Credit the fan editors whose work a cut follows, in the cut's README.

## License

The index and scripts are MIT. Each cut's repo carries its own license.
