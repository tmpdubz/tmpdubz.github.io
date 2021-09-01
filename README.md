# Personal Static Site (Summary)
- Mostly a place to hold my CV
- Generated with [Hugo](https://gohugo.io/documentation/)
- Built with GitHub actions
- Deployed with [GitHub pages](https://gohugo.io/hosting-and-deployment/hosting-on-github/)
- Uses [Minimal Themes](https://themes.gohugo.io/themes/minimal/)

# How does the deployment work?
- GitHub action triggers on push to `main`
- Builds the static site and puts it under the `gh_pages`branch
- Github Pages is deploying from the branch `gh_pages`
- It uses the CNAME file under `public/CNAME` to redirect custom domains to the GH Page

# Theme: Minimal
* Update the theme
```
git submodule update --remote themes/minimal
```

# Test locally
```
hugo server -D
```