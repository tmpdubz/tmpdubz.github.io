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