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

* To reload git submodules (you'll need to do this if you're cloning this after not touching it for a while)
```
git submodule update --init --recursive
```

# Changing Themes
If you want to change themes, you can pull a theme with a git submodule by running

```
THEME_REPO=""
NAME_OF_THEME=""
git submodule add git@github.com:${THEME_REPO}.git themes/${NAME_OF_THEME}
```

e.g.
```

THEME_REPO="nunocoracao/blowfish"
NAME_OF_THEME="blowfish"
git submodule add git@github.com:${THEME_REPO}.git themes/${NAME_OF_THEME}
```

# Test locally
```
hugo server -D
```