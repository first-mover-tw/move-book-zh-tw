---
description: Move 中的能力 (Capability) 模式：使用擁有的物件 (owned objects) 作為存取控制權杖 (access-control tokens)，以在 Sui 智慧合約 (Sui smart contracts) 中授權特殊權限操作 (privileged operations)。
title: 模式 (Pattern)：能力 (Capability)
keywords:
  - Move
  - Sui
  - Move tutorial
  - pattern
  - capability
  - abilities
  - design patterns
questions:
  - 'What is Pattern: Capability in Move?'
  - 'How do I use Pattern: Capability in Move?'
  - What is Capability is an Object in Move?
  - What is Using init for Admin Capability in Move?
answer: 'The Capability pattern in Move: use owned objects as access-control tokens to authorize privileged operations in Sui smart contracts.'
goal:
  description: 'Reader understands the Capability pattern in Move: use owned objects as access-control tokens to authorize privileged operations in Sui smart contracts'
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

# 模式：能力 (Pattern: Capability) {#pattern-capability}

在程式設計中，*能力*是一種權杖，賦予持有者執行特定動作的權利。這是一種用來控制資源與操作存取權的模式。能力的一個簡單例子是門的鑰匙。如果你有鑰匙，就可以開門；如果沒有鑰匙，就無法開門。更實際的例子是管理員能力，它允許持有者執行一般使用者無法進行的管理操作。

## 能力是一個物件 (Capability is an Object) {#capability-is-an-object}

在 [Sui 物件模型](./../object/)中，能力會表示為物件。物件擁有者可以將此物件傳入函式，以證明自己有權執行特定動作。由於嚴格型別檢查，將能力作為引數的函式只能以正確的能力呼叫。

> 慣例上會以 `Cap` 後綴為能力命名，例如 `AdminCap` 或
> `KioskOwnerCap`。

```move file=packages/samples/sources/programmability/capability.move anchor=main

```

## 使用 `init` 建立管理員能力 (Using `init` for Admin Capability) {#using-init-for-admin-capability}

常見的作法是在套件發布時建立一個唯一的 `AdminCap` 物件。如此一來，應用程式可以有一個設定階段，由管理員帳戶準備應用程式的狀態。

```move file=packages/samples/sources/programmability/capability-2.move anchor=admin_cap

```

請注意，這個 `AdminCap` 與第一個範例中的不同，僅具有 `key` 能力，前者也具有 `store`。能力的[能力](./../move-basics/abilities-introduction)定義了它如何在帳戶之間移動：具有 `key` 與 `store` 時，能力可透過公開轉移函式自由轉移，並儲存在其他物件內；僅具有 `key` 時，則只能由其模組中定義的函式轉移，因此模組可以限制，甚至完全禁止傳遞能力。如同[儲存函式](./../storage/storage-functions)章節所述，這就是內部轉移與公開轉移之間的差異。

## Sui Framework 中的能力 (Capabilities in the Sui Framework) {#capabilities-in-the-sui-framework}

能力模式不只是慣例，[Sui Framework](./sui-framework)本身即圍繞此模式建置。了解標準能力有助於你在實際原始碼中辨識此模式；以下是你最可能遇到的能力：

- `sui::coin::TreasuryCap<T>` - 與新貨幣一同建立，賦予鑄造及銷毀 `T` 型別代幣的權利。擁有 `TreasuryCap` 即代表擁有該貨幣的供應量；我們會在[餘額與代幣](./balance-and-coin)章節中探討它；
- `sui::package::UpgradeCap` - 套件發布時建立，授權未來對套件進行升級。`UpgradeCap` 的擁有者也可以限制未來升級，或透過使此能力不可變而完全停用升級；
- `sui::kiosk::KioskOwnerCap` - 賦予在 [Kiosk](https://docs.sui.io/standards/kiosk) 中對項目執行 `place`、`take` 與 `list` 的權利；Kiosk 是 Sui 的交易基元。雖然 `Kiosk` 物件本身是共享的，所有人都可存取，但對其執行「擁有者」操作時需要此能力；
- `sui::transfer_policy::TransferPolicyCap<T>` - 賦予管理 `TransferPolicy<T>` 的權利：新增與移除交易規則，以及提領收取的費用。

其中兩項能力採用型別參數，這項技巧值得注意。藉由在能力中加入[泛型](./../move-basics/generics)，其授予的權限會限定於單一型別：`TreasuryCap<GOLD>` 控制 `GOLD` 的供應量，且不會賦予對 `SILVER` 貨幣的任何權利。

框架也提供較一般形式的權限，也就是 `Publisher` 物件，用以證明對套件中所有型別的權限。此內容會在[發布者權限](./publisher)章節中另行說明。

## 地址檢查與能力的比較 (Address Check vs Capability) {#address-check-vs-capability}

將物件作為能力是區塊鏈程式設計中相對新穎的概念。在其他智慧合約語言中，授權通常是透過檢查傳送者地址完成。此模式在 Sui 上仍然可行，但整體建議使用能力，以提升安全性、可發現性及原始碼組織。

讓我們看看，如果建立使用者的 `new` 函式採用地址檢查，會是什麼樣子：

```move file=packages/samples/sources/programmability/capability-3.move anchor=with_address

```

現在來看看，相同函式使用能力後的樣子：

```move file=packages/samples/sources/programmability/capability-4.move anchor=with_capability

```

相較於地址檢查，使用能力有數項優點：

- 由於能力是物件，遷移管理員權限較為容易。若管理員地址變更，所有檢查該地址的函式都必須更新，因此需要升級套件。
- 使用能力時，函式簽名更具描述性。可清楚得知 `new` 函式需要將 `AdminCap` 作為引數傳入，而且沒有它就無法呼叫此函式。
- 物件能力不需要在函式主體中進行額外檢查，因此可降低開發者犯錯的機率。
- 擁有的能力也有助於發現權限。AdminCap 的擁有者可以在其帳戶中看到此物件（透過錢包或瀏覽器），並知道自己擁有管理員權限。使用地址檢查時，這點較不透明。

不過，地址方式也有自身的優點。其中一種情況是*多重簽章*地址：此地址由多方控制，只有在足夠多的一方簽署交易時，交易才有效。若應用程式的管理員權限屬於多重簽章地址，檢查傳送者可能比建構一筆呈現由該地址擁有的能力物件之交易更簡單。

另一種情況是，應用程式具有一個已傳入每個函式的中央物件，例如設定或登錄表。此類物件可將管理員地址儲存為一般欄位，檢查時不需要額外輸入。地址是純資料，因此可在執行階段變更，而無須升級套件。相同概念也能實現*撤銷*：已轉移的擁有能力無法從其擁有者手中取回，但中央登錄表中的項目——地址或先前發行能力的 ID——可以由管理員隨時移除，立即撤銷存取權。
