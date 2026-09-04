---
description: Sui 套件 (package) 升級：如何發佈新版本、UpgradeCap 是什麼、如何讓套件成為不可變，以及如何對共用狀態 (shared state) 進行版本控制與遷移。
title: 套件升級 (Package Upgrades)
keywords:
  - Move
  - Sui
  - Move tutorial
  - package
  - upgrades
questions:
  - What is Package Upgrades in Move?
  - How do I use Package Upgrades in Move?
  - What is An Upgrade Is a New Package in Move?
  - What Can Change?
answer: 'Package upgrades on Sui: how new versions are published, what the UpgradeCap is, how to make a package immutable, and how to version and migrate shared state.'
goal:
  description: 'Reader understands package upgrades on Sui: how new versions are published, what the UpgradeCap is, how to make a package immutable, and how to version and migrate shared state'
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

# 套件升級 (Package Upgrades) {#package-upgrades}

如同我們在 [套件](./../concepts/packages) 概念中提到的，已發布的套件是
_不可變的_——儲存在鏈上的位元組碼永遠無法被修改或刪除。然而，真實的應用程式
需要持續演進：修正錯誤、新增功能，以及更新依賴項。Sui 透過 _套件升級_
來協調這兩項需求——這是一種發布套件新版本，同時保留所有舊版本完整無缺的方法。

本節說明其運作機制：升級可以和無法變更什麼、授權升級的 `UpgradeCap` 物件，
以及——最重要的是——升級對你的套件已建立狀態意味著什麼。如需撰寫便於升級之原始碼的設計建議，請參閱
[可升級性實務](./../guides/upgradeability-practices)指南。

## 升級是新的套件 (An Upgrade Is a New Package) {#an-upgrade-is-a-new-package}

升級不會觸及已發布的位元組碼。而是會在 _新地址_ 發布新版原始碼，
並將其記錄為上一版本的後繼版本。兩個版本——事實上是曾經發布的所有版本——都會並列保留在鏈上：

```
0xAAA... <- version 1, published
0xBBB... <- version 2, upgrade of 0xAAA
0xCCC... <- version 3, upgrade of 0xBBB, the latest version
```

這帶來一個容易忽略的結果：**套件的舊版本仍可呼叫**。升級不會將任何人重新導向——交易仍可直接呼叫版本 1 的函式，
而依賴版本 1 的套件會繼續呼叫版本 1，直到它們升級自己的依賴項。單靠發布修正，
並不會阻止有錯誤的版本繼續被使用。我們會在討論[狀態](#upgrades-and-state)時回到這一點。

不過，型別不會跨版本重複建立。結構保有首次*定義*它的套件
版本身分：版本 1 的 `Counter` 型別與版本 2 中的型別完全相同，而升級前建立的物件
與新原始碼完全相容。首次在版本 2 新增的型別則屬於版本 2，依此類推。

## 可以變更什麼 (What Can Change) {#what-can-change}

升級後的套件必須與前一版本保持*相容*，確保既有呼叫端與依賴套件不會失效。
在預設——最寬鬆——的升級政策下，升級可以：

- 變更任何函式的實作；
- 新增模組、函式與型別；
- 變更、新增或移除 `public(package)`、私有及非公開的
  [`entry`](./../move-advanced/entry-functions) 函式；
- 變更依賴項。

但不能：

- 移除模組；
- 變更或移除 `public` 函式的簽章；
- 變更或移除既有型別定義——每個結構與列舉的欄位、能力與型別參數，
  無論是否公開，都會永久凍結。

簡言之：公開簽章與資料配置是永久的，實作則不是。因此，
[可升級性實務](./../guides/upgradeability-practices)指南建議將
`public` 表面維持在最小範圍，並讓結構保持精簡——每個 `public` 函式與每個結構欄位，
都是對套件整個生命週期的承諾。

## `UpgradeCap` 升級能力物件 (The `UpgradeCap`) {#the-upgradecap}

發布套件時，`Publish` 命令會回傳一個 `UpgradeCap`——這是定義在
[Sui Framework](./sui-framework) `sui::package` 模組中的物件。它是一種典型的
[能力](./capability)：持有它的人可以升級套件，其他人則不可以。

```move
module sui::package;

/// 控制升級套件能力的能力物件。
public struct UpgradeCap has key, store {
    id: UID,
    /// 可升級套件的（可變）ID。
    package: ID,
    /// 已連續套用至原始套件的升級次數。
    /// 初始值為 0。
    version: u64,
    /// 允許哪一類升級。
    policy: u8,
}
```

`package` 欄位始終指向最新版本——只有套件的最新版本可以升級，因此版本鏈永遠不會分叉。
升級本身是在單一交易內完成的三步流程：`authorize_upgrade` 接收 `UpgradeCap` 並回傳
`UpgradeTicket`；`Upgrade` 交易命令消耗票證、驗證並發布新的位元組碼，然後
回傳 `UpgradeReceipt`；最後，`commit_upgrade` 將收據套用回
`UpgradeCap`。票證與收據都是[燙手山芋](./hot-potato-pattern)——它們
無法儲存或丟棄，因此已授權的升級無法停留在未完成狀態。實務上，`sui client upgrade`
CLI 命令會為你建立整個流程。

`policy` 欄位儲存此能力物件所允許的最寬鬆升級類型。它起始為*相容*
——即[前述](#what-can-change)預設政策——且可限制為*新增式*
（只能新增功能，既有原始碼會凍結）或*僅依賴項*
（只能變更依賴項）。限制是單向的：`only_additive_upgrades` 與
`only_dep_upgrades` 可收緊政策，但沒有任何方式能將其放寬回去。並且因為
`authorize_upgrade` 是接收 `UpgradeCap` 的一般公開函式，所以可將此能力物件
包裝在自訂物件中，以強制任意升級規則——時間鎖、多重簽章或投票。

## 讓套件不可變 (Making a Package Immutable) {#making-a-package-immutable}

最終的限制是完全放棄升級。刪除 `UpgradeCap` 會讓套件成為真正不可變的套件——
再也沒有人可以發布新版本：

```move
/// 捨棄 `UpgradeCap`，使套件成為不可變。
public entry fun make_immutable(cap: UpgradeCap) {
    let UpgradeCap { id, package: _, version: _, policy: _ } = cap;
    id.delete();
}
```

這是不可逆的，而這正是重點：這是套件可以提供的最強保證。使用者與依賴套件知道，
他們審查過的原始碼就是會永遠執行的原始碼。相應的取捨也同樣永久——任何錯誤都無法再修正。
不可變性是小型基礎函式庫的常見選擇，對持續演進的應用程式而言則很危險。

## 升級與狀態 (Upgrades and State) {#upgrades-and-state}

物件儲存在套件外部，升級不會觸及它們：版本 1 建立的共享物件，版本 1 與版本 2
都同樣可以存取。加上舊版本仍可呼叫這一點，便形成升級的核心問題：
**若沒有明確的版本控制，舊原始碼會持續完整存取狀態**。若版本 2 修正了一個會修改共享物件的函式錯誤，
攻擊者只需繼續呼叫版本 1 的函式——而且是在完全相同的物件上。

解決方式是對狀態本身進行版本控制。物件帶有 `version` 欄位，套件帶有 `VERSION`
常數，而每個觸及物件的函式都會先檢查兩者是否相符：

```move file=packages/samples/sources/programmability/package-upgrades.move anchor=versioned

```

常數會嵌入位元組碼，因此每個已發布版本都會以自己的數字與物件比較：版本 1 的位元組碼檢查 `1`，
版本 2 的位元組碼檢查 `2`。只要物件欄位的值為 `1`，舊原始碼就會繼續運作，而新原始碼會中止——
一旦欄位遞增為 `2`，情況便會反轉：所有呼叫舊版本的操作都會以
`EVersionMismatch` 中止，只有最新原始碼可以繼續執行。遞增版本就是讓舊套件
*退役*的方式。

## 遷移狀態 (Migrating State) {#migrating-state}

版本遞增——即*遷移*——可透過兩種方式執行，選擇取決於狀態量以及誰能觸及它。

直接的方式是*積極式*遷移：升級後，管理員[能力](./capability)的持有者呼叫
`migrate` 函式，在單一交易中遞增共享物件的版本：

```move file=packages/samples/sources/programmability/package-upgrades.move anchor=migrate

```

積極式遷移是一次明確的切換，適用於狀態僅為發布者可控制的少數共享物件時。
當它無法觸及所有物件時便不夠適用：應用程式可能有數千個物件，或物件可能由使用者*擁有*——
而且只有擁有者可以傳送觸及已擁有物件的交易。

對於這些情況，可以使用*延遲式*遷移：不預先遷移所有內容，而是在新原始碼首次觸及每個物件時進行遷移。
這也是我們在[先前](#what-can-change)看到限制的解答——結構配置永遠不能變更，
那麼狀態要如何演進？方法是讓基礎物件保持精簡，並將實際內容儲存在
[動態欄位](./dynamic-fields)中；它可以隨時替換為新形狀：

```move file=packages/samples/sources/programmability/package-upgrades-2.move anchor=lazy

```

此套件的版本 1 將 `ConfigV1` 附加至物件；版本 2 定義了更豐富的
`ConfigV2`，並在首次存取時悄悄替換舊值。不需要協調式遷移——物件會在使用時自行升級，
無論數量是十個還是一千萬個，無論是已擁有或共享物件。

## 總結 (Summary) {#summary}

- 升級會在新地址發布套件的新版本；所有舊版本都會保留在鏈上，且*仍可呼叫*。
- 相容規則保護呼叫端：實作可以變更，也可以新增原始碼，但 `public` 函式簽章與型別定義永久不變。
- `UpgradeCap` 是授權升級的能力物件；其政策只能單向限制——從相容到新增式再到僅依賴項——
  而透過 `make_immutable` 刪除它會讓套件永久不可變。
- 狀態不是套件的一部分：若沒有明確版本控制，舊版本會持續完整存取共享物件。
  以套件 `VERSION` 常數檢查 `version` 欄位，可讓舊原始碼退役。
- 遷移可以是*積極式*——管理員在升級後立即遞增版本——或*延遲式*——
  每個物件在首次存取時遷移，這也允許透過動態欄位演進狀態的形狀。

## 延伸閱讀 (Further Reading) {#further-reading}

- 關於設計便於升級套件的[可升級性實務](./../guides/upgradeability-practices)指南。
- Sui 文件中的[套件升級](https://docs.sui.io/concepts/sui-move-concepts/packages/upgrade)。
- Sui 文件中的[自訂升級政策](https://docs.sui.io/concepts/sui-move-concepts/packages/custom-policies)。
