---
description: Move 中的能力模式（Capability Pattern）：在 Sui 智慧合約中使用擁有的物件（Owned Objects）作為存取控制權杖以授權特權操作
---

# Pattern: Capability 能力 (Pattern: Capability) {#pattern-capability}

在程式設計中，**capability（能力）**是一種賦予擁有者執行特定動作權利的權杖（token）。這是一種用來控制對資源與操作存取權的模式。能力最簡單的範例是門的鑰匙：有鑰匙就能開門，沒有鑰匙就不能開門。更實際的範例是 Admin Capability，它允許擁有者執行一般使用者無法執行的管理操作。

## Capability 是一個 Object (Capability is an Object) {#capability-is-an-object}

在 [Sui Object Model](./../object/) 中，capability 是以 object 的形式表示。object 的擁有者可以將此 object 傳入函式，以證明自己有權執行特定動作。由於嚴格的型別系統，接受 capability 作為引數的函式，只能用正確的 capability 呼叫。

> 有個慣例是以 `Cap` 後綴為 capability 命名，例如 `AdminCap` 或 `KioskOwnerCap`。

```move file=packages/samples/sources/programmability/capability.move anchor=main

```

## 使用 `init` 建立 Admin Capability (Using `init` for Admin Capability) {#using-init-for-admin-capability}

一個非常常見的做法，是在 package 發布時建立單一的 `AdminCap` object。如此一來，應用程式便能有一個設定階段，讓 admin 帳號準備好應用程式的狀態。

```move file=packages/samples/sources/programmability/capability-2.move anchor=admin_cap

```

請注意，這個 `AdminCap` 只有 `key` 能力，不像第一個範例中同時擁有 `store` 能力。capability 的[能力（abilities）](./../move-basics/abilities-introduction)定義了它如何在帳號之間移動：具備 `key` 和 `store` 時，capability 可以透過 public transfer 函式自由轉移，也能儲存在其他 object 中；只有 `key` 時，就只能透過其模組定義的函式轉移，因此模組可以限制——甚至完全禁止——這個 capability 被傳遞出去。如同[Storage Functions](./../storage/storage-functions)章節所述，這正是內部轉移與 public 轉移之間的差異。

## Sui Framework 中的 Capability (Capabilities in the Sui Framework) {#capabilities-in-the-sui-framework}

capability 模式不只是一種慣例——[Sui Framework](./sui-framework)本身就是圍繞它建立的。認識標準的 capability 有助於在實際程式碼中辨識這個模式；以下是你最可能遇到的幾種：

- `sui::coin::TreasuryCap<T>` - 與新貨幣一同建立，賦予鑄造與銷毀型別 `T` 代幣的權利。擁有 `TreasuryCap` 就是擁有該貨幣的供應量；我們會在 [Balance and Coin](./balance-and-coin) 章節深入探討；
- `sui::package::UpgradeCap` - 在 package 發布時建立，授權對該 package 的未來升級。`UpgradeCap` 的擁有者也可以限制未來的升級，或透過使該 capability 不可變（immutable）來完全停用升級；
- `sui::kiosk::KioskOwnerCap` - 賦予在 [Kiosk](https://docs.sui.io/standards/kiosk)（Sui 的交易基本元件）中 `place`、`take` 與 `list` 物品的權利。雖然 `Kiosk` object 本身是共享的（shared），任何人都能存取，但對它的「擁有者」操作需要此 capability；
- `sui::transfer_policy::TransferPolicyCap<T>` - 賦予管理 `TransferPolicy<T>` 的權利：新增與移除交易規則，以及提領已收取的費用。

其中兩個 capability 帶有型別參數——這是值得留意的技巧。透過為 capability 加上[泛型（generic）](./../move-basics/generics)，它所賦予的權限便會侷限於單一型別：`TreasuryCap<GOLD>` 只能控制 `GOLD` 的供應量，對 `SILVER` 貨幣沒有任何權利。

該 framework 也提供了一種更廣泛的權限形式——`Publisher` object，它證明了對某個 package 中所有型別的權限。這個部分會在 [Publisher Authority](./publisher) 章節中另外說明。

## 地址檢查 vs Capability (Address Check vs Capability) {#address-check-vs-capability}

將 object 用作 capability，在區塊鏈程式設計中是相對較新的概念。在其他智能合約語言中，授權通常是透過檢查發送者的地址來完成。這種模式在 Sui 上依然可行，然而，整體建議是使用 capability，以獲得更好的安全性、可發現性與程式碼組織方式。

讓我們來看看，若建立使用者的 `new` 函式改用地址檢查，會是什麼樣子：

```move file=packages/samples/sources/programmability/capability-3.move anchor=with_address

```

接著，讓我們看看同一個函式改用 capability 後的樣子：

```move file=packages/samples/sources/programmability/capability-4.move anchor=with_capability

```

相較於地址檢查，使用 capability 有幾項優勢：

- 由於 capability 是 object，管理員權限的轉移更加容易。若使用地址檢查，一旦管理員地址變更，所有檢查該地址的函式都需要更新——因而需要進行 package 升級。
- 使用 capability 時，函式簽章更具描述性。可以清楚看出 `new` 函式需要傳入 `AdminCap` 作為引數，且沒有它便無法呼叫此函式。
- Object Capability 不需要在函式主體中做額外檢查，因而降低了開發者出錯的機率。
- 擁有的 Capability 也有助於發現性。`AdminCap` 的擁有者可以在自己的帳號中看到該 object（透過錢包或瀏覽器），並知道自己擁有管理員權限。這一點在使用地址檢查時較不透明。

然而，地址檢查方式也有自己的優勢。其中一種情況是 **multisig（多重簽名）**地址——由多方共同控制的地址，只有在足夠多方簽署時，交易才算有效。若應用程式的管理員權限屬於一個 multisig 地址，檢查發送者可能會比建構一筆呈現該地址所擁有 capability object 的交易來得簡單。

另一種情況是應用程式擁有一個中央 object——例如 config 或 registry——它已經被傳入每個函式中。這樣的 object 可以將管理員地址儲存為一般欄位，檢查它不需要額外的輸入。地址是純資料，因此可以在執行期變更，不需要 package 升級。同樣的概念也讓 **revocation（撤銷）**成為可能：一個已擁有的 capability，一旦被轉移出去，就無法從其擁有者手中取回；但中央 registry 中的一筆條目——先前發出的 capability 的地址或 ID——則可以由管理員隨時移除，立即撤銷存取權。
