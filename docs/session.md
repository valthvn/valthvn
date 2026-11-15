# Session 006

The profile is one room of a museum. A gilded baroque frame holds a night scene after Van Gogh's *Starry Night Over the Rhône* (1888, public domain), the painting visitors walk into in the portfolio. Projects hang beside it as museum labels, each under the element of the scene that carries it in the portfolio: the bridge, the reflection, the lights of Arles, the strollers, the boat, the Great Bear.

The renderer and public-calendar fetcher use only Python's standard library. Every image is a self-contained SVG: brushwork is generated as rows of short strokes from seeded random numbers, so each run produces the same picture, and a turbulence displacement filter gives the static paint its wobble. Stars, lamps and reflections sit above the filtered layer and animate with plain CSS; reduced-motion preferences disable the animation. There is no JavaScript, no external image service and no link inside the images. HTML repository links and native `details` sections provide the actual interaction.

The activity panel, *The lights of Arles*, shows the last 90 observed days along the far shore. A day with at least one contribution is a light; its reflection grows with that day's contribution count (scaled to the busiest day of the window, with a 0.6 exponent so quiet days stay visible). Days without contributions stay dark; nothing is invented. The 365-day and 90-day totals are summed over the validated calendar, with the snapshot date visible. These are GitHub contributions, not exclusively commits.

No image paints a full-canvas background: the painting, the labels and the river panel carry their own surfaces, so nothing depends on the page colour. The museum labels have two variants selected by the README's `picture` elements: cream paper on the light theme, and a night-blue panel with a gold fillet on the dark theme, where cream would glare.

`PORTFOLIO_URL` in `scripts/render_session.py` is empty until the portfolio is deployed; once set, the painting becomes a link to it.

```sh
python scripts/render_session.py
python -m unittest discover -s tests -q
```

The daily workflow fetches the public calendar, regenerates the profile, tests it and commits changes. Only the current profile's source, assets, data and tests are retained.
