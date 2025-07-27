# Docs
A collection of useful commands and processes in case I don't touch this in a while and forget.

# Changing themes
* Right now I use git submodules to manage my Hugo themes.
* This can also be done with hug o modules or directly installing themes, but I find git submodules easy and there is no reason to not use it.
* If you want to change themes, you can pull a theme with a git submodule by running:
```
THEME_REPO=""
NAME_OF_THEME=""
git submodule add git@github.com:${THEME_REPO}.git themes/${NAME_OF_THEME}
```

For example:
```

THEME_REPO="nunocoracao/blowfish"
NAME_OF_THEME="blowfish"
git submodule add git@github.com:${THEME_REPO}.git themes/${NAME_OF_THEME}
```