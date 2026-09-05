---
description: Sui 儲存函式：在 Move 智慧合約中使用 `sui::transfer` 模組轉移、共享、凍結及接收物件。
title: 儲存函式 (Storage Functions)
keywords:
  - Move
  - Sui
  - Move tutorial
  - storage
  - functions
questions:
  - What is Storage Functions in Move?
  - How do I use Storage Functions in Move?
  - 'What is Ownership and References: a Quick Recap in Move?'
  - What is Internal Rule in Transfer Functions in Move?
answer: 'Sui storage functions: transfer, share, freeze, and receive objects using the sui::transfer module in Move smart contracts.'
goal:
  description: 'Reader understands sui storage functions: transfer, share, freeze, and receive objects using the sui::transfer module in Move smart contracts'
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

# 儲存函式 (Storage Functions) {#storage-functions}

定義主要儲存操作的模組是 `sui::transfer`。它會隱式匯入至所有依賴 [Sui Framework](./../programmability/sui-framework) 的套件，因此，如同其他隱式匯入的模組（例如 `std::option` 或 `std::vector`），不需要 `use` 陳述式。

> 如需快速參考，[附錄 C：轉移函式](./../appendix/transfer-functions)包含所有儲存函式與物件狀態的清單。

## 概觀 (Overview) {#overview}

`transfer` 模組會針對物件可處於的各種[擁有權狀態](./../object/ownership)，各提供一個函式：

1. [轉移](#transfer) - 將物件傳送至某個地址，使其進入 _地址擁有_ 狀態；
2. [凍結](#freeze) - 將物件設為 _不可變_ 狀態，使其成為永遠無法變更的 _公開常數_；
3. [共享](#share) - 將物件設為 _共享_ 狀態，供所有人使用。

`transfer` 模組是大多數儲存操作的首選工具。有兩種特殊情況會另外說明：[動態欄位](./../programmability/dynamic-fields) - 將資料附加至物件 - 會在下一章介紹，而[接收傳送至其他物件的物件](./transfer-to-object)則會在本章結尾介紹。

## 所有權與參考：快速回顧 (Ownership and References: a Quick Recap) {#ownership-and-references-a-quick-recap}

儲存函式直接建立於[所有權與範圍](./../move-basics/ownership-and-scope)及
[參考](./../move-basics/references)章節中的語意之上。它們全都以 _by value_ 的方式接收物件：物件會被移入函式，呼叫端將失去它——而如同我們即將看到的，它最終會以新的狀態存入儲存空間。這就是資源模型的運作方式：物件絕不會被複製到儲存空間中，而是被 _placed_ 於其中，且前一位擁有者可被證明地放棄了它。另一方面，只需要讀取或更新物件的函式，會透過參考（`&T` 或 `&mut T`）接收它，並保持所有權狀態不變。

## 轉移函式中的內部規則 (Internal Rule in Transfer Functions) {#internal-rule-in-transfer-functions}

每項儲存操作都有兩種形式：_內部_ 與 _公開_。內部函式—
`transfer`、`share_object`、`freeze_object`—會強制執行前一節的[內部限制](./internal-constraint)：它們只能在定義物件型別的模組中呼叫。以 `public_` 為前綴的公開版本則解除該限制，但除了 `key` 之外，還要求型別具有 [`store`](./store-ability)：

```move
/// 內部：只能在定義 `T` 的模組中呼叫。
public fun transfer<T: key>(obj: T, recipient: address);

/// 公開：可從任何模組呼叫，但要求 `T` 具有 `store`。
public fun public_transfer<T: key + store>(obj: T, recipient: address);
```

這兩種形式共同實作了我們在 [store 能力](./store-ability#relation-to-key)章節中預覽的規則：僅具備 `key` 的物件，其儲存完全由定義它的模組管理；而 `store` 讓任何模組都能對該物件執行儲存操作，也讓擁有者能在交易中直接進行操作。

若要一次查看所有組合，假設模組 `book::transfer_a` 定義兩個物件—具有 `key` 的 `ObjectK` 與具有 `key + store` 的 `ObjectKS`—而模組 `book::transfer_b` 嘗試轉移它們：

```move
/// 從 `transfer_a` 匯入 `ObjectK` 與 `ObjectKS` 型別，並嘗試
/// 為它們實作不同的 `transfer` 函式。
module book::transfer_b;

// 這些型別並非此模組的內部型別！
use book::transfer_a::{ObjectK, ObjectKS};

// 失敗！`ObjectK` 並非此模組的內部型別。
public fun transfer_k(k: ObjectK, to: address) {
    transfer::transfer(k, to);
}

// 失敗！`ObjectKS` 也並非此模組的內部型別—
// `store` 不會影響內部函式。
public fun transfer_ks(ks: ObjectKS, to: address) {
    transfer::transfer(ks, to);
}

// 失敗！`public_transfer` 要求 `store`，而 `ObjectK` 不具備它。
public fun public_transfer_k(k: ObjectK, to: address) {
    transfer::public_transfer(k, to);
}

// 成功！`ObjectKS` 具有 `store`，且該函式是公開的。
public fun public_transfer_ks(ks: ObjectKS, to: address) {
    transfer::public_transfer(ks, to);
}
```

相同的矩陣適用於 `share_object`/`public_share_object` 與 `freeze_object`/`public_freeze_object`。了解此規則對於理解 Move 中的應用程式設計至關重要：選擇讓物件可公開轉移（`key + store`），或將其維持為內部物件（僅具備 `key`），會大幅影響應用程式能為其資產提供的保證。

## 轉移 (Transfer) {#transfer}

`transfer::transfer` 函式會將物件傳送至一個地址，使該地址成為其唯一
擁有者：

```move
module sui::transfer;

// 將 `obj` 轉移給 `recipient`。
public fun transfer<T: key>(obj: T, recipient: address);

// `transfer` 函式的公開版本。
public fun public_transfer<T: key + store>(obj: T, recipient: address);
```

在下列範例中，模組會建立代表應用程式管理員權限的物件，
並將其傳送給模組的發布者：

```move file=packages/samples/sources/storage/storage-functions.move anchor=admin_cap

```

發布模組時，會呼叫 `init` 函式，並將其中建立的 `AdminCap` 物件
_轉移_ 給交易傳送者——`ctx.sender()` 會回傳目前交易的傳送者地址。
（[模組初始化器](./../programmability/module-initializer)章節會詳細介紹
`init` 函式。）

從此之後，假設傳送者為 `0xa11ce`，該物件便處於 _地址擁有_
狀態：只有 `0xa11ce` 能在交易中使用它——可透過參考或值使用，包括使用上述
`transfer_admin_cap` 函式進一步轉移它。

> 地址擁有的物件受到 _真正所有權_ 的約束——只有擁有者地址可以存取它們。
> 這是 Sui 儲存模型中的基本概念，會在
> [所有權](./../object/ownership#account-owner-or-single-owner)章節中介紹。

### 公開轉移 (Public Transfer) {#public-transfer}

讓我們透過一個函式擴充此範例；該函式使用 `AdminCap` 授權鑄造新物件，
並將其轉移至任意地址：

```move file=packages/samples/sources/storage/storage-functions.move anchor=mint_and_transfer

```

任何人「都可以」呼叫 `mint_and_transfer` 函式——它是公開的——但它要求將
`AdminCap` 參考作為第一個引數，而 `AdminCap` 物件僅由 `0xa11ce`
擁有。因此在實務上，只有 `0xa11ce` 能夠鑄造。這種簡單且明確的函式存取
控制方式，就是 _[能力模式](./../programmability/capability)_，也是 Sui
應用程式設計的基石之一。

請注意此範例中兩個物件的差異。`AdminCap` 僅具備 `key`：模組對它保有完整
控制權；如果模組未公開 `transfer_admin_cap` 函式，管理員權限便會是
_靈魂綁定_ 的——無法交付給他人。`Gift` 具有 `key + store`：它會透過
`public_transfer` 傳送，而無論誰擁有 `Gift`，都能在自己的交易中自由地將其
進一步轉移，無須此模組提供任何協助。

### 重點回顧 (Quick Recap) {#quick-recap}

- `transfer` 會將物件傳送至地址，使其成為 _地址擁有_；
- 只有擁有者能使用地址擁有的物件——可透過參考或值使用；
- 將僅具備 `key` 的物件作為引數，可將函式存取權限限制為該物件的擁有者——
  _能力_ 模式；
- `public_transfer` 是公開形式：可在任何位置呼叫，並要求 `key + store`。

## 凍結 (Freeze) {#freeze}

`transfer::freeze_object` 函式會將物件置於 _不可變_ 狀態。物件一旦被 _凍結_，便永遠無法變更，且任何人都能透過不可變參考存取它：

```move
module sui::transfer;

// 使物件不可變，並允許任何人讀取它。
public fun freeze_object<T: key>(obj: T);

// `freeze_object` 函式的公開版本。
public fun public_freeze_object<T: key + store>(obj: T);
```

讓我們以管理員建立並凍結的 `Config` 物件來擴充目前的範例：

```move file=packages/samples/sources/storage/storage-functions.move anchor=config

```

呼叫 `create_and_freeze` 後，`Config` 會透過其 ID 公開可用，而且任何人都能呼叫 `message` 函式——對於凍結物件而言，取得不可變參考不受限制。

函式定義不會與物件狀態綁定，因此，_定義_ 接受凍結型別的可變參考或值的函式完全合法——只是無法以凍結物件來*呼叫*它們：

```move file=packages/samples/sources/storage/storage-functions.move anchor=frozen_uncallable

```

以下 [Share](#share) 章節中定義的 `delete_config` 也是如此：它以值的方式接收 `Config`，而凍結的 `Config` 永遠無法傳入其中。凍結是*永久性*的：凍結物件無法被修改、轉移、刪除，也無法解除凍結。

### 已擁有 → 已凍結 (Owned → Frozen) {#owned-frozen}

由於 `freeze_object` 的簽章會以值的方式接受任何物件，它可以接收在相同作用域中建立的物件，也可以接收傳送者*擁有*的物件。可以將單一擁有者轉換為不可變狀態！例如，`Gift` 的擁有者可以決定永久保存它：

```move file=packages/samples/sources/storage/storage-functions.move anchor=freeze_gift

```

基於顯而易見的安全理由，反方向也必須留意：絕不能凍結 `AdminCap`——凍結的能力會讓所有人都能讀取，而每個由 `&AdminCap` 控制存取的函式都會變成任何人皆可呼叫。這再次顯示僅限 `key` 模式的價值：`AdminCap` 沒有 `store`，因此外部原始碼無法凍結它，且模組也沒有公開凍結函式。

### 快速回顧 (Quick Recap) {#quick-recap-1}

- `freeze_object` 會將物件永久置於*不可變*狀態；
- 任何人都能透過不可變參考讀取凍結物件，且它永遠無法被修改、轉移或刪除；
- 已擁有的物件可以被凍結——若物件具有 `store`，其擁有者也能在交易中將其凍結；
- `public_freeze_object` 是公開形式：可在任何地方呼叫，並要求 `key + store`。

## 分享 (Share) {#share}

`transfer::share_object` 函式會將物件置於*共享*狀態，此時任何人都可以透過可變（因此也包括不可變）參考來存取它：

```move
module sui::transfer;

/// 將物件置於共享狀態——所有人皆可存取。
public fun share_object<T: key>(obj: T);

/// `share_object` 函式的公開版本。
public fun public_share_object<T: key + store>(obj: T);
```

```move file=packages/samples/sources/storage/storage-functions.move anchor=share

```

不同於可接受新建與已擁有物件的 `freeze_object`，`share_object` 有一項執行期限制：**只有在同一筆交易中建立的物件可以共享**。嘗試共享已存在於已擁有狀態的物件時，會以 `ESharedNonNewObject` 中止。不存在 Owned → Shared 轉換：是否要讓物件共享，必須在建立時決定。如同凍結，分享也是單向的——一旦共享，物件在其餘生命週期中都會維持共享狀態，只有一個例外，接下來會說明。

### 特殊情況：共享物件刪除 (Special Case: Shared Object Deletion) {#special-case-shared-object-deletion}

雖然共享物件通常無法以值的方式取得，但有一個特殊情況可以——當取得它的函式會將其*刪除*時。這是 Sui 儲存模型中的特殊情況，用於清理共享狀態。讓我們新增一個刪除共享 `Config` 的函式：

```move file=packages/samples/sources/storage/storage-functions.move anchor=delete_shared

```

`delete_config` 函式會以值的方式取得 `Config` 並將其完全銷毀——解構 struct 並刪除 `UID`——Sui Verifier 允許此呼叫。然而，若該函式回傳 `Config`，或嘗試對其執行 `transfer` 或 `freeze`，交易將遭拒絕：

```move
// 無法運作！
public fun transfer_shared(c: Config, to: address) {
    transfer::transfer(c, to);
}
```

規則是：以值的方式取得共享物件時，必須在同一筆交易中將其刪除。

### 快速回顧 (Quick Recap) {#quick-recap-2}

- `share_object` 會將物件置於*共享*狀態，所有人皆可透過可變參考存取；
- 只有在同一筆交易中建立的物件可以共享——不存在 Owned → Shared 轉換；
- 分享是永久性的，僅有一個例外：共享物件可為了將其*刪除*而以值的方式取得；
- `public_share_object` 是公開形式：可在任何地方呼叫，要求 `key + store`。

## 派對轉移 (Party Transfer) {#party-transfer}

`transfer` 模組也提供 `party_transfer` 和 `public_party_transfer`，可將物件置於[派對狀態](./../object/ownership#party-objects)中——具備共識排序的單一擁有者存取。派對物件是較新且進階的功能，因此未納入持續範例；函式簽名列於[附錄 C](./../appendix/transfer-functions#party)，詳細內容則於 [`sui::party`](https://docs.sui.io/references/framework/sui/party) 模組文件中說明。

## 總結 (Summary) {#summary}

| 函式             | 最終狀態 | 可逆？                                               | 公開版本                |
| ---------------- | -------- | ---------------------------------------------------- | ----------------------- |
| `transfer`       | 地址擁有 | 是 - 轉移出去                                        | `public_transfer`       |
| `freeze_object`  | 不可變   | 否                                                   | `public_freeze_object`  |
| `share_object`   | 共享     | 僅能透過刪除                                         | `public_share_object`   |
| `party_transfer` | Party    | [取決於權限](./../appendix/transfer-functions#party) | `public_party_transfer` |

- 每個儲存函式都以 _by value_ 的方式接收物件——將物件放入儲存空間會消耗該物件；
- 內部版本要求該型別必須定義於呼叫模組中；`public_*` 版本則
  改為要求 `store`。

## 後續步驟 (Next Steps) {#next-steps}

現在你已了解 `transfer` 模組的主要功能，可以開始建置涉及儲存操作的應用程式。在下一節中，我們會介紹 [UID 與 ID](./uid-and-id) 型別——每個物件的身分識別——接著介紹 [以物件形式接收](./transfer-to-object)，這是物件擁有其他物件背後的機制。

## 延伸閱讀 (Further Reading) {#further-reading}

- [`sui::transfer`](https://docs.sui.io/references/framework/sui/transfer) 模組文件。
- [附錄 C：轉移函式](./../appendix/transfer-functions)。
