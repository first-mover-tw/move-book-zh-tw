---
description: Sui 上升級 Move 套件（package）的最佳實務：維持相容性、規劃版本管理，並避免破壞性變更 (Breaking Changes)。
---

# 升級性最佳實踐 (Upgradeability Practices) {#upgradeability-practices}

> 本指南建立在 [套件升級 (Package Upgrades)](./../programmability/package-upgrades) 章節之上，該章節
> 說明了升級的機制：版本、`UpgradeCap`，以及狀態遷移。

要討論升級性的最佳實踐，我們首先需要理解套件中哪些部分可以被升級。
升級性的基本前提是：升級不應破壞與前一版本的公開相容性。
可被依賴套件使用的模組部分，其靜態簽名不應改變。這適用於模組——模組不能從
套件中移除、公開結構——它們可能被用於函式簽名中，以及公開
函式——它們可以被其他套件呼叫。

```move
// module 不能從 package 移除
module book::upgradable;

// dependencies 可以更改（如果它們沒有在公開簽章中使用）
use std::string::String;
use sui::event; // can be removed

// public structs 不能移除，也不能更改
public struct Book has key {
    id: UID,
    title: String,
}

// 相同規則適用於 event structs
public struct BookCreated has copy, drop {
    /* ... */
}

// public functions 不能移除，且它們的簽章永遠不能更改
// 但是實作可以更改
public fun create_book(ctx: &mut TxContext): Book {
    create_book_internal(ctx)

    // 可以移除和更改
    event::emit(BookCreated {
        /* ... */
    })
}

// package-visibility functions 可以移除和更改
public(package) fun create_book_package(ctx: &mut TxContext): Book {
    create_book_internal(ctx)
}

// entry functions 只要不是 public 就可以移除和更改
entry fun create_book_entry(ctx: &mut TxContext): Book {
    create_book_internal(ctx)
}

// private functions 可以移除和更改
fun create_book_internal(ctx: &mut TxContext): Book {
    abort
}
```

<!--
## Using entry and friend functions

TODO: Add a section about entry and friend functions
-->

## 物件版本控制 (Versioning objects) {#versioning-objects}

<!-- This practice is for function version locking based on a shared state -->

為了淘汰套件的舊版本，物件可以被版本化。只要物件
包含一個版本欄位，且使用該物件的程式碼會預期並斷言特定版本，
程式碼就可以被強制遷移到新版本。通常，在升級之後，管理員函式可以
被用來更新共享狀態的版本，讓新版本的程式碼可以被使用，而
舊版本的程式碼則會因版本不符而中止。

```move
module book::versioned_state;

const EVersionMismatch: u64 = 0;

const VERSION: u8 = 1;

/// 共享狀態（也可以被擁有）
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

## 使用動態欄位進行配置版本控制 (Versioning configuration with dynamic fields) {#versioning-configuration-with-dynamic-fields}

<!-- This practice is for versioning the contents / structure of objects -->

Sui 中有一個常見的模式，允許在保留相同物件簽名的情況下，
變更物件所儲存的配置。做法是保持基礎物件簡單且版本化，
再將實際的配置物件以動態欄位的形式加入。使用這種「錨點 (anchor)」
模式，配置可以隨套件升級而改變，同時保持相同的基礎物件簽名。

```move
module book::versioned_config;

use sui::vec_map::VecMap;
use std::string::String;

/// 基礎物件
public struct Config has key {
    id: UID,
    version: u16
}

/// 實際的配置
public struct ConfigV1 has store {
    data: Bag,
    metadata: VecMap<String, String>
}

// ...
```

<!-- ## Modular architecture -->

<!-- TODO: add two patterns for modular architecture: object capability (SuiFrens) and witness registry (SuiNS) -->
