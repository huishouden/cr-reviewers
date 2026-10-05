# Huishouden cr reviewers

Specialized [`cr`](https://github.com/open-cli-collective/codereview-cli) review agents for the
Huishouden suite: the ten apps on one site, the kit (`@huishouden/pwa-kit`), `huishouden/rules` and
the Workers. Each one judges a pull request against a rule the suite lives by, the part a CI check
can't decide. Generic reviewers (language, security, architecture) come from your other agent
sources; these add the Huishouden lanes on top.

## Reviewers

| Agent | Tier | Checks |
|---|---|---|
| `huishouden:docs-sync` | medium | The docs that describe a change moved with it: README features, screenshots and setup, the release entry, the kit's STANDARD.md, DESIGN.md and docs/, the portal's `apps.json` and privacy page, the rules README, the org profile, the suite's skills and CLI docs |
| `huishouden:design-language` | medium | UI against pwa-kit DESIGN.md: names, the app bar frame, light and dark colour roles, kit components, completion, copy tone, logos |
| `huishouden:i18n` | medium | Text in English, Spanish and Dutch together, the glossary's words, whole-sentence messages, kit formatters, stored text in every language |
| `huishouden:roles-privacy` | large | Data visible only as roles allow (admin, member, helper, kid); money and health never to helpers or kids; private flags, personal audiences, contact pay details; enforced by the rules; nothing personal to analytics |
| `huishouden:public-data` | large | Real or inferable personal data in a public repo: fixtures, sample data, staging seeds, comments, docs, screenshots |
| `huishouden:shared-kit` | medium | Copies of what the kit provides, and generic code two apps share that belongs in the kit |

Each reviewer returns no findings outside a Huishouden repository, so the source is safe to add to a
profile that also reviews other projects.

## Use it

Clone it **outside** any app checkout: `cr` refuses agent sources inside the worktree of the pull
request it is reviewing, so a reviewer can't be changed by the code under review.

```sh
git clone https://github.com/huishouden/cr-reviewers ~/Dev/huishouden-cr-reviewers
cr config agent-source add ~/Dev/huishouden-cr-reviewers/.codereview/agents --profile <profile>
cr agents list --profile <profile>        # the huishouden:* agents, from this source
cr review <PR URL> --profile <profile> --dry-run
```

In a Huishouden repo, `hh dev review` (huishouden/cli) runs the same review on a draft PR with this
source. Pull the clone to pick up changes; `cr` reads the prompts at review time. When two sources define
the same agent id, the source listed later on the profile wins (`cr agents show huishouden:docs-sync`
names the source in use).

## Add or change a reviewer

Layout is the `cr` agent catalog format:

```
.codereview/agents/huishouden/
  index.yaml                 # the group: name, description, owner
  <agent>/index.yaml         # name (= folder), description, model_tier, effort, file_globs, applies_when
  <agent>/prompt.md          # the codereview-cli output contract, scope, the rule, severity
```

- `model_tier` is `small`, `medium` or `large` and `effort` `low`, `medium` or `high`; an unknown tier
  aborts every review at planning time, not just this agent's.
- A reviewer reports what its own lane owns, even where another might also notice it; no "owned by"
  lines. Prefer 0–5 findings; a clean diff earns none.
- Cite the suite's own source of truth (pwa-kit STANDARD.md, DESIGN.md, docs/, the rules README) and
  say that the repository's copy wins over the prompt's summary, so a prompt can lag a little without
  misleading.
- List the agent in the table above.

Before a PR is ready (pull requests run no hosted CI):

```sh
python3 scripts/validate-agents.py   # structure, tiers, README listing
cr agents list --profile <profile> --agents-dir .codereview/agents
```

and a `cr review … --dry-run` on a Huishouden PR the reviewer should catch.

## History

`huishouden:design-language`, `huishouden:public-data` and `huishouden:shared-kit` were first written
in `piekstra/cr-reviewer-catalog` (`.codereview/agents/huishouden/`) and moved here, updated for the
current suite, when the Huishouden reviewers became the org's own.

## License

Source available under [PolyForm Shield 1.0.0](LICENSE): you may use, study and modify this code
for any purpose except providing a product that competes with Huishouden.

Huishouden and its logo are the project's brand; please don't use them for other products.
