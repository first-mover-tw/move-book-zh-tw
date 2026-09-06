---
title: 編譯模式 (Compilation Modes) | 參考手冊
description: Move 編譯模式 (Move compilation modes) 參考：定義具名建置模式 (named build modes)、篩選宣告 (declarations)，並設定模式專屬編譯 (mode-specific compilation)。
keywords:
  - Move
  - Sui
  - Move reference
  - compilation
  - modes
  - reference
questions:
  - How does Compilation Modes work in Move?
  - What is the syntax for Compilation Modes in Move?
  - What is Mode Basics in Move?
  - What is Mode Names in Move?
answer: 'Move compilation modes reference: define named build modes, filter declarations, and configure mode-specific compilation.'
goal:
  description: 'Reader understands move compilation modes reference: define named build modes, filter declarations, and configure mode-specific compilation'
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

# 編譯模式 (Compilation Modes) {#compilation-modes}

模式是在編譯時期控制建置中包含哪些宣告的具名切換開關。

- `#[mode(name1, name2, ...)]` 依已啟用的模式名稱篩選宣告。
- `#[test_only] ≡ #[mode(test)]`。
- 未加註解的宣告一律會被包含。
- 加上註解的宣告，當且僅當列出的任一名稱已啟用時才會被包含。
- 啟用任何模式（包括 test）代表該建置不可發布。
- 模式僅影響編譯時期的包含；除了可發布性以外，它們會在位元碼層級被消除。

## 模式基礎 (Mode Basics) {#mode-basics}

模式透過以下屬性表示：

```move
#[mode(name1, name2, ...)]

#[test_only] //（`#[mode(test)]` 的簡寫）
```

以啟用任何模式（包括 test）的方式編譯的程式碼不可發布。

本節定義模式的語法、包含規則、範圍與工具互動方式。（如需包含範例的入門教學，請參閱指南頁面。）

### 模式註解 (Mode Annotations) {#mode-annotations}

`#[mode(...)]` 可放在模組與模組成員（函式、結構、常數等）上。

```move
#[mode(name1, name2, ...)]
module <addr_opt>::<ident> { ... }

module <addr_opt>::<ident> {
    #[mode(name1, name2, ...)]
    <decl>
}
```

> **注意**：`#[test_only]` 與 `#[mode(test)]` 完全等價。

## 模式名稱 (Mode Names) {#mode-names}

每個名稱都是非空白識別字。模式名稱會區分大小寫。

## 包含模型 (Inclusion model) {#inclusion-model}

令 `M` 為建置已啟用模式的集合。令 `S(m)` 為宣告 `m` 上列出的模式集合，其中 `#[test_only]` 會貢獻 `{test}`，而未加註解的宣告具有 `S(x) = ∅`。宣告 x 當且僅當符合下列其中一項時，才會被包含在編譯單元中：

- `S(x) = ∅`（未加註解）
- `S(x) ∩ M ≠ ∅:`（包含註解）

也就是說：未加註解的宣告一律會被包含；加上註解的宣告，當且僅當建置中至少啟用了其列出名稱之一時才會被包含，否則將被排除。

### 模組範圍 (Module scope) {#module-scope}

若模組被排除，其所有成員也會隱含地被排除。若模組被包含，若加上註解的成員本身 `S(m)` 未與 `M` 相交，仍可能被排除。

### 單一屬性上的多個模式 (Multiple modes on one attribute) {#multiple-modes-on-one-attribute}

`#[mode(a, b, c)]` 中的清單為析取（邏輯 OR）：只要任一列出的名稱相符，就會被包含。

## 名稱解析與重複項目 (Name resolution & duplicates) {#name-resolution-duplicates}

模式僅為編譯時期篩選器。它們不會引入執行時期條件判斷，且在位元碼中沒有表示方式。所有驗證都會在原始碼中被包含的子集上執行。

若出現重複項目，會套用標準名稱解析規則。這表示兩個模式不得在同一建置中啟用具有相同名稱的不同模組或成員。同樣地，加上模式註解的定義不得覆寫同名的未加註解宣告。

若要提供特定模式的替代方案，請將它們放在由模式控制的獨立模組中，或使用不同名稱並在測試或驅動程式中選取它們。

## 使用工具與旗標 (Usage Tooling & flags) {#usage-tooling-flags}

建置與測試時，`move build --mode <name>` 會將 `<name>` 加入 `M`。可重複傳入 `--mode` 以啟用多個模式；`M` 是所有傳入名稱的聯集，例如 `move build --mode test --mode debug`。這會啟用以 `#[mode(test)]` 或 `#[mode(debug)]` 註解的所有模組與成員。請注意，`move test` 會隱含提供 `--mode test`。

## 可發布性 (Publishability) {#publishability}

任何啟用至少一個模式（包括 test）的建置，都會產生不可發布的輸出。若要建立可發布的成品，不得啟用任何模式。
