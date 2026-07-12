---
description:
  Sui 的套件升級 (Package Upgrades)：新版本如何發布、UpgradeCap 是什麼、如何讓套件變成不可變 (immutable)，以及如何為共享狀態
  (shared state) 進行版本控制與遷移 (migrate)
---

# 套件升級 (Package Upgrades) {#package-upgrades}

正如我們在[套件](./../concepts/packages)概念中提到的，已發布的套件是**不可變的**——儲存在鏈上的位元組碼永遠無法被修改或刪除。然而實際的應用程式需要演進：修復錯誤、新增功能、依賴項也會往前推進。Sui 透過**套件升級**來調和這兩個需求——一種在保留每個先前版本完整不變的情況下，發布套件新版本的方式。

本節說明其運作機制：升級可以改變什麼、不能改變什麼、授權升級的 `UpgradeCap` 物件，以及——最重要的——升級對套件已經建立的狀態意味著什麼。關於撰寫適合升級的程式碼的設計建議，請參閱[升級性實踐](./../guides/upgradeability-practices)指南。

## 升級即是新套件 (An Upgrade Is a New Package) {#an-upgrade-is-a-new-package}

升級不會觸及已發布的位元組碼。相反地，它會在**新地址**發布新版本的程式碼，並將其記錄為前一版本的後繼者。所有版本——事實上，所有曾經發布過的版本——都會並存於鏈上：

```
0xAAA... <- version 1, published
0xBBB... <- version 2, upgrade of 0xAAA
0xCCC... <- version 3, upgrade of 0xBBB, the latest version
```

這帶來一個容易被忽略的後果：**套件的舊版本仍然可以被呼叫**。升級並不會重新導向任何人——一筆交易仍然可以直接呼叫第 1 版的函式，而依賴第 1 版的套件在升級自己的依賴項之前，會持續呼叫第 1 版。發布修復本身並不會阻止有問題的版本被使用。我們在談到[狀態](#upgrades-and-state)時會回到這一點。

然而，型別並不會在各版本間重複建立。一個結構體會保留最初**定義**它的套件版本的身分：第 1 版中的 `Counter` 型別，在第 2 版中完全就是同一個型別，且升級前建立的物件與新程式碼完全相容。首次在第 2 版新增的型別屬於第 2 版，依此類推。

## 什麼可以改變 (What Can Change) {#what-can-change}

升級後的套件必須與前一版本保持**相容**，才不會破壞既有呼叫者與依賴套件。在預設——也是最寬鬆的——升級政策下，升級可以：

- 改變任何函式的實作；
- 新增模組、函式與型別；
- 改變、新增或移除 `public(package)`、私有以及非公開的
  [`entry`](./../move-advanced/entry-functions) 函式；
- 改變依賴項。

而且不能：

- 移除模組；
- 改變或移除 `public` 函式的簽章；
- 改變或移除既有的型別定義——每個結構體與列舉的欄位、能力（abilities）與型別參數，無論公開與否，都永遠被凍結。

簡而言之：公開簽章與資料佈局是永久的，實作則不是。這正是為什麼[升級性實踐](./../guides/upgradeability-practices)指南建議保持 `public` 介面最小化並讓結構體精簡——每個 `public` 函式與每個結構體欄位，都是對套件生命週期的一項承諾。

## `UpgradeCap` 升級能力憑證 (The `UpgradeCap`) {#the-upgradecap}

當套件被發布時，`Publish` 命令會回傳一個 `UpgradeCap`——這是定義於 [Sui Framework](./sui-framework) 的 `sui::package` 模組中的物件。它是一個經典的[能力（capability）](./capability)：擁有它的人可以升級套件，其他人則不行。

```move
module sui::package;

/// 控制升級套件能力的 Capability。
public struct UpgradeCap has key, store {
    id: UID,
    /// （可變）可被升級的套件 ID。
    package: ID,
    /// （可變）已套用在原始套件上的
    /// 累計升級次數。初始為 0。
    version: u64,
    /// 允許哪種類型的升級。
    policy: u8,
}
```

`package` 欄位永遠指向最新版本——只有套件的最新版本可以被升級，因此版本鏈永遠不會分叉。升級本身是在單一交易中進行的三步驟流程：`authorize_upgrade` 接收 `UpgradeCap` 並回傳 `UpgradeTicket`；`Upgrade` 交易命令消耗此 ticket，驗證並發布新的位元組碼，然後回傳 `UpgradeReceipt`；最後，`commit_upgrade` 將此 receipt 套用回 `UpgradeCap`。ticket 與 receipt 都是[熱馬鈴薯（hot potatoes）](./hot-potato-pattern)——它們無法被儲存或丟棄，因此一個已授權的升級不能被留在半完成狀態。實務上，整個流程都由 `sui client upgrade` CLI 命令為你建構完成。

`policy` 欄位儲存此能力所允許的最寬鬆升級種類。它一開始是**相容（compatible）**——即[前述](#what-can-change)的預設政策——並可以被限制為**僅新增（additive）**（只能新增新功能，既有程式碼被凍結）或**僅依賴項（dependency-only）**（只能改變依賴項）。限制是單向道：`only_additive_upgrades` 與 `only_dep_upgrades` 可以收緊政策，但沒有任何方法可以將其放寬回去。而且因為 `authorize_upgrade` 是一個接收 `UpgradeCap` 的普通公開函式，此能力可以被包裝在自訂物件中，以強制執行任意的升級規則——時間鎖、多重簽章，或投票機制。

## 讓套件不可變 (Making a Package Immutable) {#making-a-package-immutable}

最終的限制是完全放棄升級能力。刪除 `UpgradeCap` 會讓套件真正變成不可變——沒有人將能再發布新版本：

```move
/// 丟棄 `UpgradeCap` 以使套件變成不可變。
public entry fun make_immutable(cap: UpgradeCap) {
    let UpgradeCap { id, package: _, version: _, policy: _ } = cap;
    id.delete();
}
```

這是不可逆的，而這正是重點所在：這是套件所能提供的最強保證。使用者與依賴套件都能知道他們審查過的程式碼，就是永遠會執行的程式碼。這個取捨同樣是永久的——任何錯誤都永遠無法被修復。對於小型基礎函式庫來說，不可變性是常見的選擇；但對於持續演進的應用程式而言，則是危險的選擇。

## 升級與狀態 (Upgrades and State) {#upgrades-and-state}

物件儲存在套件之外，升級不會觸及它們：由第 1 版建立的共享物件，對第 1 版與第 2 版來說都同樣可存取。再加上舊版本仍然可以被呼叫這個事實，這就導致了升級的核心問題：**若沒有明確的版本控制，舊程式碼將保留對狀態的完整存取權**。如果第 2 版修復了一個會修改共享物件的函式中的錯誤，攻擊者可以直接持續呼叫第 1 版的函式——針對同一個物件。

解決方案是為狀態本身加上版本控制。物件攜帶一個 `version` 欄位，套件攜帶一個 `VERSION` 常數，每個觸及該物件的函式都會先檢查這兩者是否相符：

```move file=packages/samples/sources/programmability/package-upgrades.move anchor=versioned

```

常數會被烘焙進位元組碼中，因此每個已發布版本都會用自己的編號來比對物件：第 1 版的位元組碼檢查是否為 `1`，第 2 版的位元組碼檢查是否為 `2`。只要物件的欄位仍是 `1`，舊程式碼就能持續運作，而新程式碼則會中止（abort）——而一旦該欄位被提升為 `2`，情況就會反轉：每次呼叫舊版本都會以 `EVersionMismatch` 中止，只有最新的程式碼能夠繼續執行。提升版本正是舊套件被**淘汰（decommissioned）**的方式。

## 遷移狀態 (Migrating State) {#migrating-state}

版本提升——也就是**遷移（migration）**——可以透過兩種方式進行，選擇取決於狀態的數量以及誰能夠觸及它。

直截了當的方式是**積極式（eager）**遷移：在升級完成後，管理[能力（capability）](./capability)的持有者立即呼叫 `migrate` 函式，在單一交易中提升共享物件的版本：

```move file=packages/samples/sources/programmability/package-upgrades.move anchor=migrate

```

積極式遷移是一次乾淨俐落的切換，當狀態只是發布者所掌控的少數幾個共享物件時，這是正確的選擇。但當它無法觸及所有物件時，這個方式就顯得不足：一個應用程式可能有數千個物件，或者這些物件可能由使用者**擁有**——而只有擁有者才能送出觸及自己所擁有物件的交易。

對於這些情況，有**惰性（lazy）**遷移：不是預先遷移所有東西，而是在新程式碼首次觸及每個物件時才進行遷移。這同時也回答了我們[稍早](#what-can-change)看到的一個限制——結構體佈局永遠無法改變，那麼狀態究竟該如何演進？作法是讓基礎物件保持精簡，並將實際內容儲存在[動態欄位](./dynamic-fields)中，這樣就可以隨時替換成新的形態：

```move file=packages/samples/sources/programmability/package-upgrades-2.move anchor=lazy

```

此套件的第 1 版為物件附加了 `ConfigV1`；第 2 版則定義了更豐富的 `ConfigV2`，並在首次存取時悄悄地替換掉舊值。不需要協同的遷移——物件會在被使用時自我升級，無論是十個還是一千萬個，無論是自己擁有的還是共享的。

## 總結 (Summary) {#summary}

- 升級會在新地址發布套件的新版本；所有先前版本都會保留在鏈上，且**仍然可以被呼叫**。
- 相容性規則保護呼叫者：實作可以改變，新程式碼也可以被新增，但 `public` 函式簽章與型別定義是永久的。
- `UpgradeCap` 是授權升級的能力；其政策只能單向收緊——從相容到僅新增再到僅依賴項——透過 `make_immutable` 將其刪除，會讓套件永遠不可變。
- 狀態不屬於套件的一部分：若沒有明確的版本控制，舊版本會保留對共享物件的完整存取權。將 `version` 欄位與套件的 `VERSION` 常數進行比對檢查，即可淘汰舊程式碼。
- 遷移可以是**積極式**的——管理員在升級後立即提升版本——也可以是**惰性**的——每個物件在首次存取時自我遷移，這也讓狀態的形態能夠透過動態欄位演進。

## 延伸閱讀 (Further Reading) {#further-reading}

- [升級性實踐](./../guides/upgradeability-practices)指南，關於設計適合升級的套件。
- Sui 文件中的[套件升級](https://docs.sui.io/concepts/sui-move-concepts/packages/upgrade)。
- Sui 文件中的[自訂升級政策](https://docs.sui.io/concepts/sui-move-concepts/packages/custom-policies)。
