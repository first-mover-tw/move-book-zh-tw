---
description: 理解 Move 封裝 (Move packages) — 程式碼組織的單位，包含模組 (modules)、相依性 (dependencies) 和發佈於 Sui 區塊鏈 (Sui blockchain) 上的地址 (addresses)。
title: 套件 (Package)
keywords:
  - Move
  - Sui
  - Move tutorial
  - package
questions:
  - What is Package in Move?
  - How do I use Package in Move?
  - What is Package Structure in Move?
  - What is Published Package in Move?
answer: Understand Move packages — the unit of code organization containing modules, dependencies, and addresses published on the Sui blockchain.
goal:
  description: Reader understands Move packages — the unit of code organization containing modules, dependencies, and addresses published on the Sui blockchain
  requires:
    - has_frontmatter:
        - title
        - description
        - keywords
      label: Has required frontmatter fields
    - min_words: 50
      label: Needs content depth
    - has_questions: true
      label: Needs questions for AI search visibility
    - has_answer: true
      label: Needs answer summary for AI citation
---

# 套件 (Package) {#package}

Move 是一種用來撰寫智慧合約的語言——這些程式被儲存在區塊鏈上並執行。
單一程式會被組織成一個套件。一個套件會被發布到區塊鏈上，並由一個[地址](./address)來識別。透過發送呼叫其函式的[交易](./what-is-a-transaction)，可以與已發布的套件進行互動。它也可以作為其他套件的相依性。

> 若要建立新套件，請使用 `sui move new` 指令。若要深入了解該指令，請執行
> `sui move new --help`。

一個套件由多個模組組成——這些是包含函式、型別和其他項目的獨立範圍。

```
package 0x...
    module a
        struct A1
        fun hello_world()
    module b
        struct B1
        fun hello_package()
```

## 套件結構 (Package Structure) {#package-structure}

在本機上，一個套件是一個包含 `Move.toml` 檔案與 `sources` 目錄的資料夾。`Move.toml` 檔案（稱為「套件資訊清單」）包含關於該套件的後設資料，而 `sources` 目錄則包含模組的原始程式碼。一個套件通常看起來像這樣：

```
sources/
    my_module.move
    another_module.move
    ...
tests/
    ...
examples/
    using_my_module.move
Move.toml
```

`tests` 目錄是選填的，其中包含該套件的測試。放入 `tests` 目錄中的程式碼不會被發布到鏈上，且僅在測試中可用。`examples` 目錄可用於程式碼範例，同樣也不會被發布到鏈上。

## 已發布套件 (Published Package) {#published-package}

在開發期間，套件尚未擁有地址，此時會以 `0x0` 代替。一旦套件被發布後，它會在區塊鏈上獲得一個獨特的[地址](./address)，其中包含其模組的位元組碼。已發布的套件會變成_不可變的 (immutable)_，並且可以透過發送交易來與其互動。

```
0x...
    my_module: <bytecode>
    another_module: <bytecode>
```

雖然已發布的位元組碼永遠無法被修改，但套件可以進行_升級_：升級會在新的地址發布新版本的套件，同時保留舊版本。我們將在本書中探討相關的影響：[套件升級 (Package Upgrades)](./../programmability/package-upgrades)章節說明了其運作機制，而[可升級性實務指南 (Upgradeability Practices)](./../guides/upgradeability-practices)則涵蓋了如何為升級進行設計。

## 延伸閱讀 (Further Reading) {#further-reading}

- [套件資訊清單 (Package Manifest)](./manifest)
- [地址 (Address)](./address)
- Move 參考手冊中的[套件 (Packages)](./../../reference/packages)。
