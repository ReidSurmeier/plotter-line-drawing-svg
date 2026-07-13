# Issue tracker: GitHub

Issues and PRDs for this repository live in GitHub Issues. Run `gh` commands
inside this clone so the CLI infers `ReidSurmeier/plotter-line-drawing-svg` from
the remote.

## Conventions

- Create: `gh issue create --title "..." --body "..."`
- Read: `gh issue view <number> --comments`
- List: `gh issue list --state open --json number,title,body,labels`
- Comment: `gh issue comment <number> --body "..."`
- Label: `gh issue edit <number> --add-label "..."`
- Close: `gh issue close <number> --comment "..."`

When a skill says “publish to the issue tracker,” create a GitHub issue. When a
skill says “fetch the relevant ticket,” read the issue and its comments.
