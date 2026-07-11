---
description: 'Sui storage functions: transfer, share, freeze, and receive objects using the sui::transfer module in Move smart contracts.'
---

# 存儲函式 (Storage Functions)

一旦定義了 [具有 `key` 能力](./key-ability.md) 的結構，它就可以與 Sui 的「存儲函式 (storage functions)」一起使用。這些函式在 `sui::transfer` 模組中定義，並提供了一種在 Sui 上管理物件生命週期、所有權和存取權限的方法。

## 轉移模組 (Transfer Module)

`sui::transfer` 模組是 Sui 框架的核心組成部分。它提供了基本的操作來處理物件：

- `transfer`：將物件的所有權轉移給一個地址。
- `freeze_object`：使物件變為不可變（凍結）。
- `share_object`：將物件變為共享物件，任何人都可以存取。

### 公開與私有轉移 (Public vs Private Transfer)

`transfer` 模組為每個函式提供了兩個版本：一個是「私有的」，要求類型 `T` 僅具有 `key`；另一個是「公開的」，要求 `T` 同時具有 `key` 和 `store`。

1. **私有轉移**：僅能在定義該類型的模組內部呼叫。這允許開發者強制執行自定義的轉移邏輯（例如：版稅、限制）。
2. **公開轉移**：任何人都可以呼叫。如果一個類型具有 `store`，則可以使用以 `public_` 為前綴的版本。

我們將在 [能力：Store](./store-ability.md) 章節中更深入地探討這一點。

## 轉移至地址 (Transfer to Address) {#transfer}

最常見的操作是將物件轉移給一個地址（使用者或另一個物件）。一旦轉移，物件就歸該地址所有。

```move
module sui::transfer;

/// 將物件轉移給一個地址。僅在定義 `T` 的模組中可用。
public native fun transfer<T: key>(obj: T, recipient: address);

/// 公開版本的 `transfer` 函式。可用於任何具有 `key + store` 的 `T`。
public native fun public_transfer<T: key + store>(obj: T, recipient: address);
```

### 範例：發行管理能力 (AdminCap)

通常在 `init` 函式中，我們會建立一個管理能力物件並將其發送給部署者：

```move
public struct AdminCap has key { id: UID }

fun init(ctx: &mut TxContext) {
    let admin_cap = AdminCap { id: object::new(ctx) };
    transfer::transfer(admin_cap, ctx.sender());
}
```

## 不可變物件 (Frozen Objects)

`freeze_object` 函式用於將物件變為不可變。一旦物件被凍結，它就永遠不能被更改、刪除或轉移。任何人都可以透過不可變參考來讀取它。

```move
module sui::transfer;

/// 將物件變為不可變並允許任何人讀取它。
public native fun freeze_object<T: key>(obj: T);

/// 公開版本的 `freeze_object` 函式。
public native fun public_freeze_object<T: key + store>(obj: T);
```

### 範例：建立並凍結配置 (Config)

讓我們擴展之前的範例，並添加一個允許管理員建立 `Config` 物件並凍結它的函式：

```move
/// 管理員可以「建立並凍結」的某種 `Config` 物件。
public struct Config has key {
    id: UID,
    message: String
}

/// 建立一個新的 `Config` 物件並將其凍結。
public fun create_and_freeze(
    _: &AdminCap,
    message: String,
    ctx: &mut TxContext
) {
    let config = Config {
        id: object::new(ctx),
        message
    };

    // 凍結物件使其變為不可變。
    transfer::freeze_object(config);
}

/// 從 `Config` 物件返回訊息。
/// 可以透過不可變參考存取該物件！
public fun message(c: &Config): String { c.message }
```

一旦物件被凍結，它就可以被任何人透過不可變參考存取。`Config` 內容現在透過其 ID 公開可用，任何人都可以讀取。

> 注意：函式定義與物件的狀態無關。您可以定義一個接收可變參考的函式，但它無法在已凍結的物件上被呼叫。

## 共享物件 (Shared Objects)

`share_object` 函式用於將物件放入「共享 (shared)」狀態。一旦物件被共享，任何人都可以透過可變參考（當然也包括不可變參考）來存取它。

```move
module sui::transfer;

/// 將物件放入共享狀態 —— 可以以可變和不可變方式存取。
public native fun share_object<T: key>(obj: T);

/// 公開版本的 `share_object` 函式。
public native fun public_share_object<T: key + store>(obj: T);
```

### 共享物件的刪除

雖然共享物件通常不能按值獲取，但有一種特殊情況可以 —— 如果接收它的函式刪除了該物件。

```move
/// 建立一個新的 `Config` 物件並共享它。
public fun create_and_share(message: String, ctx: &mut TxContext) {
    let config = Config {
        id: object::new(ctx),
        message
    };

    // 共享物件。
    transfer::share_object(config);
}

/// 刪除 `Config` 物件，按值獲取。
/// 可以在共享物件上呼叫！
public fun delete_config(c: Config) {
    let Config { id, message: _ } = c;
    id.delete()
}
```

## 總結

- `transfer`：將所有權轉移給地址。
- `freeze_object`：使物件永久變為不可變且公開可讀。
- `share_object`：使物件變為共享，任何人都可以可變地存取。
- 所有函式都有對應的 `public_` 版本，用於具有 `store` 能力的類型。

## 下一步

現在您已經了解了 `transfer` 模組的主要功能，您可以開始在 Sui 上建立涉及存儲操作的更複雜的應用程式。在下一章中，我們將介紹 [Store 能力](./store-ability)，它允許將資料存儲在物件內部並放寬轉移限制。之後，我們將介紹 [UID 和 ID](./uid-and-id) 類型，它們是 Sui 存儲模型中最重要的類型。

[key]: ./key-ability.md
[store]: ./store-ability.md
