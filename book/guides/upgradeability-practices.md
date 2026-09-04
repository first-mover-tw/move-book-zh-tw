---
description: 在 Sui 上升級 Move 套件 (packages) 的最佳實務：維持相容性、規劃版本控制，並避免破壞性變更。
title: 可升級性實務 (Upgradeability Practices)
keywords:
  - Move
  - Sui
  - Move tutorial
  - upgradeability
  - practices
  - abilities
  - upgrades
questions:
  - What is Upgradeability Practices in Move?
  - How do I use Upgradeability Practices in Move?
  - What is Using entry and friend functions in Move?
  - What is Versioning objects in Move?
answer: 'Best practices for upgrading Move packages on Sui: maintain compatibility, plan for versioning, and avoid breaking changes.'
goal:
  description: 'Reader understands best practices for upgrading Move packages on Sui: maintain compatibility, plan for versioning, and avoid breaking changes'
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

# 可升級性實務 (Upgradeability Practices) {#upgradeability-practices}

> 本指南以 [套件升級](./../programmability/package-upgrades)章節為基礎，該章節
> 說明了升級的機制：版本、`UpgradeCap` 與狀態遷移。

在討論可升級性的最佳實務之前，我們首先需要了解套件中有哪些內容可以升級。
可升級性的基本前提是，升級不應破壞與前一版本的公開相容性。相依套件可使用的模組
部分不應變更其靜態簽名。這適用於模組——模組不可從套件中移除；公開結構——它們可用於
函式簽名；以及公開函式——它們可由其他套件呼叫。

```move
// 模組不可從套件中移除
module book::upgradable;

// 可以變更依賴項（若未用於公開簽名）
use std::string::String;
use sui::event; // 可以移除

// 公開結構不可移除，也不可變更
public struct Book has key {
    id: UID,
    title: String,
}

// 相同規則也適用於事件結構
public struct BookCreated has copy, drop {
    /* ... */
}

// 公開函式不可移除，且其簽名永遠不可變更
// 但可以變更實作
public fun create_book(ctx: &mut TxContext): Book {
    create_book_internal(ctx)

    // 可以移除及變更
    event::emit(BookCreated {
        /* ... */
    })
}

// 套件可見性函式可以移除及變更
public(package) fun create_book_package(ctx: &mut TxContext): Book {
    create_book_internal(ctx)
}

// 只要不是公開函式，入口函式可以移除及變更
entry fun create_book_entry(ctx: &mut TxContext): Book {
    create_book_internal(ctx)
}

// 私有函式可以移除及變更
fun create_book_internal(ctx: &mut TxContext): Book {
    abort
}
```

<!--
## 使用入口與 friend 函式 (Using entry and friend functions)

TODO：新增關於入口與 friend 函式的章節
-->

## 物件版本控制 (Versioning objects) {#versioning-objects}

<!-- 此實務用於依據共用狀態進行函式版本鎖定 -->

若要淘汰套件的舊版本，可以對物件進行版本控制。只要物件包含版本欄位，且使用該物件的
程式碼預期並斷言特定版本，即可強制將程式碼遷移至新版本。通常在升級後，可使用管理員函式
更新共用狀態的版本，使新版本程式碼得以使用，而舊版本則因版本不符而中止。

```move
module book::versioned_state;

const EVersionMismatch: u64 = 0;

const VERSION: u8 = 1;

/// 共用狀態（也可以由帳戶擁有）
public struct SharedState has key {
    id: UID,
    version: u8,
    /* ... */
}

public fun mutate(state: &mut SharedState) {
    assert!(state.version == VERSION, EVersionMismatch);
    // ...
}
```

## 使用動態欄位進行設定版本控制 (Versioning configuration with dynamic fields) {#versioning-configuration-with-dynamic-fields}

<!-- 此實務用於對物件的內容／結構進行版本控制 -->

Sui 有一種常見模式，可在保留相同物件簽名的同時變更物件儲存的設定。其作法是保持基礎物件
簡單且具有版本控制，並將實際的設定物件新增為動態欄位。使用此 _錨點_ 模式，可透過套件
升級變更設定，同時維持相同的基礎物件簽名。

```move
module book::versioned_config;

use sui::vec_map::VecMap;
use std::string::String;

/// 基礎物件
public struct Config has key {
    id: UID,
    version: u16
}

/// 實際設定
public struct ConfigV1 has store {
    data: Bag,
    metadata: VecMap<String, String>
}

// ...
```

<!-- ## 模組化架構 (Modular architecture) -->

<!-- TODO：新增兩種模組化架構模式：物件能力（SuiFrens）與見證登錄（SuiNS） -->
