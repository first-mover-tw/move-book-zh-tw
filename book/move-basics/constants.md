---
description: Move 中的常數 (Constants)：如何定義不可變的模組層級值、命名慣例，以及支援的常數類型。
title: 常數 (Constants)
keywords:
  - Move
  - Sui
  - Move tutorial
  - constants
questions:
  - What is Constants in Move?
  - How do I use Constants in Move?
  - What is Naming Convention in Move?
  - What is Constants Are Immutable in Move?
answer: 'Constants in Move: how to define immutable module-level values, naming conventions, and supported constant types.'
goal:
  description: 'Reader understands constants in Move: how to define immutable module-level values, naming conventions, and supported constant types'
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

# 常數 (Constants) {#constants}

常數是在模組層級定義的不可變值。它們通常用來為整個模組中使用的靜態值命名。例如，若產品有預設價格，你可能會為其定義常數。常數儲存在模組的位元組碼中，每次使用時都會複製其值。如同每個模組成員，常數預設為私有；但與函式或結構不同的是，它們無法設為公開。下方的[設定模式](#using-the-config-pattern)說明如何在模組之間共用它們。

```move file=packages/samples/sources/move-basics/constants-shop-price.move anchor=shop_price

```

## 命名慣例 (Naming Convention) {#naming-convention}

常數必須以大寫字母開頭，這會在編譯器層級強制執行。對於作為值使用的常數，慣例是全部使用大寫字母，並以底線分隔單字，讓常數在原始碼中與其他識別字有所區別。[錯誤常數](./assert-and-abort#error-constants)是例外，它們會以 `E` 開頭，後接 CamelCase 描述，例如 `ENoAccess`。

```move file=packages/samples/sources/move-basics/constants-naming.move anchor=naming

```

## 常數不可變 (Constants Are Immutable) {#constants-are-immutable}

常數無法變更或指派新值。作為套件位元組碼的一部分，它們本質上不可變。

```move
module book::immutable_constants;

const ITEM_PRICE: u64 = 100;

// 產生錯誤
fun change_price() {
    ITEM_PRICE = 200;
}
```

## 使用設定模式 (Using the Config Pattern) {#using-the-config-pattern}

應用程式常見的使用情境是定義一組在整個原始碼庫中使用的常數。但由於常數對模組而言是私有的，其他模組無法存取它們。解決方法之一是定義一個「設定」模組，透過公開函式匯出常數：

```move file=packages/samples/sources/move-basics/constants-config.move anchor=config

```

如此一來，其他模組便能匯入並讀取這些常數，且更新流程也會簡化。若需要變更常數，只需在套件升級時更新設定模組。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考資料中的[常數](./../../reference/constants)
- [常數的程式碼撰寫慣例](./../guides/code-quality-checklist#regular-constants-are-all_caps)
