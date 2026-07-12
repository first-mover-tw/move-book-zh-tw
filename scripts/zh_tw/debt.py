"""Legacy body 債務清單（單一權威：check_repo 的 exit code 與
tests/test_baseline.py 的不變式共用）。

使用者裁決（2026-07-11 tier 決策）：這些檔案的 body 是 backfill 前的舊
譯文（A 層只換 frontmatter），其中的違禁詞/簡體殘留與使用者的 reference/
翻譯 WIP（stash acb51154）重疊，不機器重譯、待人工清理。

清理一檔就從清單移除一檔；清單外的任何違規都是新問題，check_repo 會紅。
2026-07-12 實測 16 檔。
"""

LEGACY_BODY_DEBT = frozenset({
    "book/appendix/glossary.md",
    "book/appendix/transfer-functions.md",
    "book/your-first-move/hello-world.md",
    "reference/constants.md",
    "reference/control-flow.md",
    "reference/control-flow/labeled-control-flow.md",
    "reference/control-flow/loops.md",
    "reference/equality.md",
    "reference/extensions.md",
    "reference/friends.md",
    "reference/functions.md",
    "reference/functions/macros.md",
    "reference/method-syntax.md",
    "reference/packages.md",
    "reference/primitive-types/vector.md",
    "reference/structs.md",
})
