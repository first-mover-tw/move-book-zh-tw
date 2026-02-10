# 模式：能力 (Pattern: Capability)

在程式設計中，「能力 (Capability)」是一種授權持有者執行特定動作的權杖 (token)。這是一種用於控制資源和操作存取權限的模式。能力的一個簡單例子是門的鑰匙：如果您有鑰匙，就可以開門；如果您沒有鑰匙，就無法開門。一個更實際的例子是「管理員能力 (Admin Capability)」，它允許持有者執行普通使用者無法執行的管理操作。

## 能力即物件

在 [Sui 物件模型](./../object/) 中，能力被表示為物件。物件的擁有者可以將該物件傳遞給函式，以證明其具有執行特定操作的權利。由於嚴格的類型檢查，接收能力作為參數的函式只能使用正確的能力進行呼叫。

> 慣例上，能力的名稱會以 `Cap` 為後綴，例如 `AdminCap` 或 `KioskOwnerCap`。

```move file=packages/samples/sources/programmability/capability.move anchor=main

```

## 使用 `init` 建立管理員能力

一種非常常見的做法是在套件發佈時建立一個單一的 `AdminCap` 物件。這樣，應用程式可以有一個「設置階段 (setup phase)」，由管理員帳戶準備應用程式的狀態。

```move file=packages/samples/sources/programmability/capability-2.move anchor=admin_cap

```

## 地址檢查 vs 能力 (Address Check vs Capability)

利用物件作為能力是區塊鏈程式設計中一個相對較新的概念。在其他智慧合約語言中，授權通常是透過檢查發送者的地址來執行的。這種模式在 Sui 上仍然可行，但總體建議是使用能力，以獲得更好的安全性、可發現性和程式碼組織。

讓我們先看看如果使用地址檢查，建立使用者的 `new` 函式會是什麼樣子：

```move file=packages/samples/sources/programmability/capability-3.move anchor=with_address

```

現在，讓我們看看使用能力的同一個函式會是什麼樣子：

```move file=packages/samples/sources/programmability/capability-4.move anchor=with_capability

```

使用能力相比地址檢查有幾個優點：

- **遷移更容易**: 由於能力是物件，管理權限的遷移更加容易。如果使用地址檢查，一旦管理員地址變更，所有檢查該地址的函式都需要更新——因此需要進行套件升級。
- **函式簽名更具描述性**: 使用能力時，函式簽名更加明確。很明顯，`new` 函式需要傳入 `AdminCap` 作為參數，且沒有它就無法呼叫該函式。
- **減少錯誤**: 物件能力不需要在函式體內進行額外的檢查，因此減少了開發人員犯錯的機會。
- **可發現性 (Discoverability)**: 擁有的能力也有助於探索。`AdminCap` 的擁有者可以在其帳戶中（透過錢包或瀏覽器）看到該物件，並知道自己擁有管理權限。這在地址檢查中不太透明。

然而，地址檢查的方法也有其優點。例如，如果地址是多簽 (multisig) 的，且交易構建變得更加複雜，則檢查地址可能會更容易。此外，如果應用程式有一個在每個函式中都會使用的核心物件，它可以在其中存儲管理員地址，這將簡化遷移。對於「可撤銷能力 (revocable capabilities)」，核心物件的方法也很有價值，管理員可以從使用者那裡撤銷能力。
