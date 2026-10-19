def short_sha:
  if test("^[0-9a-f]{40}$") then .[:12] else . end;

.changes[0] as $primary |
{
  title: "chore(\(.package)): \($primary.before | short_sha) -> \($primary.after | short_sha)",
  body: (
    [
      "| Pin | Before | After |",
      "| --- | --- | --- |",
      (.changes[] | "| \(.name) | `\(.before)` | `\(.after)` |"),
      "",
      "[Upstream changes](\(.upstream))"
    ] + (
      if (.notes // "") != "" then
        ["", (.notes | split("\n") | map("> " + .) | join("\n"))]
      else
        []
      end
    ) | join("\n") + "\n"
  )
}
