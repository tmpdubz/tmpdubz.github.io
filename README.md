# Personal Static Site (Summary)
- Mostly a place to hold my CV
- Generated with [Hugo](https://gohugo.io/documentation/)
- Built with GitHub actions
- Deployed with [GitHub pages](https://gohugo.io/hosting-and-deployment/hosting-on-github/)

# How does the deployment work?
- GitHub action triggers on push to `main`
- Builds the static site and puts it under the `gh_pages`branch
- Github Pages is deploying from the branch `gh_pages`
- It uses the CNAME file under `public/CNAME` to redirect custom domains to the GH Page, so don't delete that

# Theme: [Blowfish](https://blowfish.page/)
* Blowfish has their own tooling written in javascript: `blowfish-tools`
* We can add that as an npm dev depedency and script some useful npm commands
```
npm run dev → Start local Hugo dev server

npm run build → Build static site for deployment

npm run init → Initialize theme config files

npm run update → Update theme assets

npm run help → Show all available blowfish-tools commands
```

* To reload git submodules (you'll need to do this if you're cloning this after not touching it for a while)
```
git submodule update --init --recursive
```
## Resume and PDF

Edit `content/resume/index.md` for both the website and downloadable CV.

```sh
npm run build   # Regenerate the PDF, then build Hugo
npm run pdf     # Regenerate static/Tomasz-Dubiel-CV.pdf only
```

The PDF exporter uses Python 3 with no third-party dependencies and embeds the bundled
Open Sans fonts from `static/fonts/open-sans/` (license included). The website uses the
same fonts. Deployment regenerates
the PDF before building the site. Commit the updated PDF with resume changes so the
download is also available when running `npm run dev`. The resume page includes a
print action with a light layout for browser printing or saving as PDF.

Homepage content and layout live in `content/_index.md` and
`layouts/partials/home/custom.html`. Local theme customizations live in `layouts/`
and `assets/css/custom.css`; the Blowfish submodule is unchanged.
