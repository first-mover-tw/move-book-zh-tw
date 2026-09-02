---
description: Sui 儲存函式 (Sui storage functions)：在 Move 智能合約中使用 sui::transfer 模組來轉移 (transfer)、共享 (share)、凍結 (freeze) 與接收 (receive) 物件。
---

# 儲存函式 (Storage Functions) {#storage-functions}

定義主要儲存操作的模組是 `sui::transfer`。它在所有依賴 [Sui Framework](./../programmability/sui-framework) 的套件中都會被隱式引入，因此，就像其他隱式引入的模組（例如 `std::option` 或 `std::vector`）一樣，不需要 `use` 陳述式。

> 快速參考請見 [附錄 C：轉移函式 (Appendix C: Transfer Functions)](./../appendix/transfer-functions)，其中列出了所有儲存函式與物件狀態。

## 總覽 (Overview) {#overview}

`transfer` 模組為物件可以進入的每一種
[所有權狀態](./../object/ownership) 都提供了對應的函式：

1. [轉移 (Transfer)](#transfer) - 將物件傳送給某個地址，使其進入 _address owned_（地址擁有）狀態；
2. [凍結 (Freeze)](#freeze) - 將物件置於 _immutable_（不可變）狀態，使其成為永遠不會改變的 _public constant_（公開常數）；
3. [共享 (Share)](#share) - 將物件置於 _shared_（共享）狀態，讓所有人都能存取。

`transfer` 模組是大多數儲存操作的首選工具。有兩個特殊情況將另外說明：下一章的 [動態欄位 (Dynamic Fields)](./../programmability/dynamic-fields) — 將資料附加到物件上，以及本章末尾的 [接收傳送給其他物件的物件](./transfer-to-object)。

## 擁有權與參考：快速回顧 (Ownership and References: a Quick Recap) {#ownership-and-references-a-quick-recap}

儲存函式直接建立在
[擁有權與作用域](./../move-basics/ownership-and-scope) 及
[參考](./../move-basics/references) 章節的語意之上。所有這些函式都以*傳值*方式接收物件：
物件被移入函式中，呼叫者失去該物件的擁有權 — 而且，如我們即將看到的，該物件最終會以新的狀態進入儲存。這正是資源模型的運作方式：物件永遠不會被複製進儲存，而是被*放置*到儲存中，且先前的擁有者確實地放棄了它。另一方面，只需要讀取或更新物件的函式，則以參考的方式接收（`&T` 或 `&mut T`），並保持擁有權狀態不變。

## Transfer 函式中的內部規則 (Internal Rule in Transfer Functions) {#internal-rule-in-transfer-functions}

每個儲存操作都有兩種形式：_internal_（內部）和 _public_（公開）。內部函式 -
`transfer`、`share_object`、`freeze_object` - 強制執行前一節的
[internal constraint](./internal-constraint)（內部約束）：它們只能在定義該物件型別的模組中被呼叫。公開版本 -
以 `public_` 為前綴 - 解除這個限制，但要求該型別除了 `key` 之外還要有
[`store`](./store-ability)：

```move
/// 內部：只能在定義 `T` 的模組中呼叫。
public fun transfer<T: key>(obj: T, recipient: address);

/// 公開：可以從任何模組呼叫，但要求 `T` 具有 `store`。
public fun public_transfer<T: key + store>(obj: T, recipient: address);
```

這兩種形式共同實作了我們在
[store ability](./store-ability#relation-to-key) 一節中預覽過的規則：只有 `key` 的物件的儲存，完全由其定義模組掌控，而
`store` 則讓該物件可以被任何模組執行儲存操作 - 以及由擁有者在交易中直接操作。

為了一次看清所有組合，假設模組 `book::transfer_a` 定義了兩個物件 - 具有
`key` 的 `ObjectK` 與具有 `key + store` 的 `ObjectKS` - 而模組 `book::transfer_b` 嘗試轉移
它們：

```move
/// 從 `transfer_a` 匯入 `ObjectK` 與 `ObjectKS` 型別，並嘗試
/// 為它們實作不同的 `transfer` 函式。
module book::transfer_b;

// 這些型別對本模組來說並非內部！
use book::transfer_a::{ObjectK, ObjectKS};

// 失敗！`ObjectK` 不是本模組的內部型別。
public fun transfer_k(k: ObjectK, to: address) {
    transfer::transfer(k, to);
}

// 失敗！`ObjectKS` 也不是本模組的內部型別 —
// `store` 不會影響內部函式。
public fun transfer_ks(ks: ObjectKS, to: address) {
    transfer::transfer(ks, to);
}

// 失敗！`public_transfer` 要求 `store`，而 `ObjectK` 沒有它。
public fun public_transfer_k(k: ObjectK, to: address) {
    transfer::public_transfer(k, to);
}

// 成功！`ObjectKS` 具有 `store`，而且這個函式是公開的。
public fun public_transfer_ks(ks: ObjectKS, to: address) {
    transfer::public_transfer(ks, to);
}
```

同樣的矩陣也適用於 `share_object`/`public_share_object` 以及
`freeze_object`/`public_freeze_object`。理解這條規則，對於理解 Move 中的
應用程式設計至關重要：讓一個物件可公開轉移（`key + store`）與保持內部（僅
`key`）之間的抉擇，會大幅影響應用程式對其資產所能提供的保證。

## Transfer 轉移 (Transfer) {#transfer}

`transfer::transfer` 函式會將物件送到某個地址，讓該地址成為其唯一擁有者：

```move
module sui::transfer;

// 將 `obj` 轉移給 `recipient`。
public fun transfer<T: key>(obj: T, recipient: address);

// `transfer` 函式的公開版本。
public fun public_transfer<T: key + store>(obj: T, recipient: address);
```

在以下範例中，模組建立了一個代表應用程式管理員權限的物件，並將它送給模組的發布者：

```move file=packages/samples/sources/storage/storage-functions.move anchor=admin_cap

```

當模組被發布時，`init` 函式會被呼叫，其中建立的 `AdminCap` 物件會被*轉移*給交易的發送者 —— `ctx.sender()` 會回傳目前交易的發送者地址。（`init` 函式在[模組初始化器](./../programmability/module-initializer)章節中有詳細說明。）

從此之後，假設發送者是 `0xa11ce`，該物件就處於*地址擁有*狀態：只有 `0xa11ce` 能在交易中使用它——無論是透過參考或值傳遞，包括用上方的 `transfer_admin_cap` 函式繼續轉移它。

> 地址擁有的物件受*真正擁有權*約束——只有擁有者地址能存取它們。這是 Sui 儲存模型中的基本概念，已在[擁有權](./../object/ownership#account-owner-or-single-owner)章節中介紹過。

### 公開轉移 (Public Transfer) {#public-transfer}

讓我們擴充範例，加入一個使用 `AdminCap` 來授權鑄造新物件並將其轉移給任意地址的函式：

```move file=packages/samples/sources/storage/storage-functions.move anchor=mint_and_transfer

```

`mint_and_transfer` 函式「理論上」任何人都能呼叫——它是公開的——但它要求第一個參數必須是 `AdminCap` 參考，而 `AdminCap` 物件是由 `0xa11ce` 獨自擁有的。所以實際上只有 `0xa11ce` 能鑄造。這種簡單明確的方式來限制對函式的存取，就是*[能力模式](./../programmability/capability)*，是 Sui 應用程式設計的基石之一。

注意這個範例中兩個物件的差異。`AdminCap` 只有 `key`：模組對它保有完全的控制權，如果模組沒有公開 `transfer_admin_cap` 函式，管理員權限就會是*靈魂綁定*的——無法轉讓出去。`Gift` 則具有 `key + store`：它是用 `public_transfer` 送出的，任何擁有 `Gift` 的人都能在自己的交易中自由地繼續轉移它，不需要這個模組的任何協助。

### 快速回顧 (Quick Recap) {#quick-recap}

- `transfer` 會將物件送到某個地址，使其成為*地址擁有*；
- 只有擁有者能使用地址擁有的物件——無論是透過參考或值傳遞；
- 要求一個只有 `key` 的物件作為參數，能將函式的存取權限制在物件擁有者身上——這就是*能力*模式；
- `public_transfer` 是公開版本：任何地方都能呼叫，但要求 `key + store`。

## 凍結 (Freeze) {#freeze}

`transfer::freeze_object` 函式會把物件轉為 _不可變_ 狀態。物件一旦被
_凍結_，就永遠無法改變，任何人都可以透過不可變參考存取它：

```move
module sui::transfer;

// 讓物件變成不可變，並允許任何人讀取它。
public fun freeze_object<T: key>(obj: T);

// `freeze_object` 函式的公開版本。
public fun public_freeze_object<T: key + store>(obj: T);
```

讓我們用一個由管理員建立並凍結的 `Config` 物件來延伸這個範例：

```move file=packages/samples/sources/storage/storage-functions.move anchor=config

```

一旦呼叫 `create_and_freeze`，`Config` 就會透過其 ID 公開可用，任何人都能呼叫
`message` 函式 —— 對於一個凍結的物件，不可變參考是人人都能自由取用的。

函式的定義與物件的狀態無關，因此定義一個以可變參考或以值取用凍結型別的函式，
在語法上完全合法 —— 只是這些函式**無法**用凍結物件來呼叫：

```move file=packages/samples/sources/storage/storage-functions.move anchor=frozen_uncallable

```

同樣的規則也適用於下方[分享 (Share)](#share) 段落中定義的 `delete_config`：它以值取用
`Config`，而一個凍結的 `Config` 永遠無法傳入其中。凍結是*永久性*的：
一個凍結的物件無法被修改、轉移、刪除 —— 也無法解凍。

### 單一擁有者 → 凍結 (Owned → Frozen) {#owned-frozen}

由於 `freeze_object` 的簽章接受任何以值傳入的物件，它既可以接收在同一作用域中
建立的物件，也可以接收發送者*擁有*的物件。從單一擁有者轉換為不可變狀態是可行的！
舉例來說，`Gift` 的擁有者可以決定將它永久保存：

```move file=packages/samples/sources/storage/storage-functions.move anchor=freeze_gift

```

出於顯而易見的安全考量，反方向的情況也同樣值得留意：`AdminCap` 絕不能被凍結
—— 一旦被凍結的權限物件，就會變成任何人都可讀取，而每個以 `&AdminCap` 把關的
函式也會變成任何人都能呼叫。這再次凸顯了僅使用 `key` 這種模式的價值：`AdminCap`
沒有 `store`，外部程式碼無法將它凍結，而模組本身也根本不對外提供凍結函式。

### 快速回顧 (Quick Recap) {#quick-recap-1}

- `freeze_object` 會把物件轉為*不可變*狀態 —— 且是永久性的；
- 凍結的物件可供任何人透過不可變參考讀取，且永遠無法被修改、轉移或刪除；
- 已擁有的物件可以被凍結 —— 若物件具有 `store`，甚至可以由擁有者在交易中凍結；
- `public_freeze_object` 是公開版本：可在任何地方呼叫，但要求 `key + store`。

## 分享 (Share) {#share}

`transfer::share_object` 函式會將物件放入 _共享_ 狀態，讓任何人都能透過可變參考（因此也包含不可變參考）存取它：

```move
module sui::transfer;

/// 將物件放入共享狀態 — 讓所有人都能存取。
public fun share_object<T: key>(obj: T);

/// `share_object` 函式的公開版本。
public fun public_share_object<T: key + store>(obj: T);
```

```move file=packages/samples/sources/storage/storage-functions.move anchor=share

```

與同時接受新物件及已擁有物件的 `freeze_object` 不同，`share_object` 有一項執行期限制：**只有在同一筆交易中建立的物件才能被共享**。若嘗試共享一個已存在於擁有狀態的物件，交易會以 `ESharedNonNewObject` 中止。並不存在 Owned → Shared 的轉換：是否要讓物件成為共享狀態，必須在物件建立時就決定。而且和凍結一樣，共享是單向的——一旦共享，物件在其餘生都會維持共享狀態，唯一的例外我們接下來會看到。

### 特殊案例：共享物件的刪除 (Special Case: Shared Object Deletion) {#special-case-shared-object-deletion}

雖然共享物件通常無法以值的方式取用，但有一種特殊情況例外——如果取用它的函式會將其**刪除**。這是 Sui 儲存模型中的一個特殊案例，用來允許清理共享狀態。讓我們新增一個刪除共享 `Config` 的函式：

```move file=packages/samples/sources/storage/storage-functions.move anchor=delete_shared

```

`delete_config` 函式以值的方式取用 `Config`，並將其完全銷毀——解構該結構並刪除 `UID`——Sui 驗證器允許這樣的呼叫。然而，若該函式回傳了 `Config`，或嘗試 `transfer` 或 `freeze` 它，交易就會被拒絕：

```move
// 行不通！
public fun transfer_shared(c: Config, to: address) {
    transfer::transfer(c, to);
}
```

規則：以值取用的共享物件，必須在同一筆交易中被刪除。

### 快速回顧 (Quick Recap) {#quick-recap-2}

- `share_object` 會將物件放入 _共享_ 狀態，讓任何人都能透過可變參考存取；
- 只有在同一筆交易中建立的物件才能被共享——不存在 Owned → Shared 的轉換；
- 共享是永久性的，唯一的例外：共享物件可以被以值取用，以便進行 _刪除_；
- `public_share_object` 是公開形式：可在任何地方呼叫，需要 `key + store`。

## Party Transfer 派對轉移 (Party Transfer) {#party-transfer}

`transfer` 模組還提供了 `party_transfer` 和 `public_party_transfer`，可將物件放入
[party 狀態](./../object/ownership#party-objects) —— 具備共識排序的單一擁有者存取模式。Party 物件是進階的較新功能，我們將其排除在本範例之外；函式簽名列於
[附錄 C](./../appendix/transfer-functions#party)，詳細內容則涵蓋於
[`sui::party`](https://docs.sui.io/references/framework/sui/party) 模組文件中。

## 總結 (Summary) {#summary}

| 函式             | 結果狀態 | 是否可逆                                             | 公開版本                |
| ---------------- | -------- | ---------------------------------------------------- | ----------------------- |
| `transfer`       | 地址擁有 | 是 - 可以再轉走                                      | `public_transfer`       |
| `freeze_object`  | 不可變   | 否                                                   | `public_freeze_object`  |
| `share_object`   | 共享     | 只能透過刪除                                         | `public_share_object`   |
| `party_transfer` | Party    | [取決於權限](./../appendix/transfer-functions#party) | `public_party_transfer` |

- 每個儲存函式都是以**傳值**方式接收物件——把物件放進儲存中會消耗它；
- 內部版本要求該型別必須定義在呼叫的模組中；`public_*` 版本則要求該型別具備 `store` 能力。

## 下一步 (Next Steps) {#next-steps}

現在你已經了解 `transfer` 模組的主要功能，可以開始建構涉及儲存操作的應用程式了。在下一節中,我們會介紹 [UID 與 ID](./uid-and-id) 型別——每個物件的身分——之後則是 [接收為物件 (Receiving as Object)](./transfer-to-object),也就是物件擁有其他物件背後的機制。

## 進階閱讀 (Further Reading) {#further-reading}

- [`sui::transfer`](https://docs.sui.io/references/framework/sui/transfer) 模組文件。
- [附錄 C：轉移函式 (Appendix C: Transfer Functions)](./../appendix/transfer-functions)。
