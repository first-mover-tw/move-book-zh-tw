---
description: Sui 中的物件擁有權類型 (Object ownership types)：單一擁有者、共享狀態、不可變物件，以及物件擁有的物件，並附上範例說明。
title: 所有權 (Ownership)
keywords:
  - Move
  - Sui
  - Move tutorial
  - ownership
questions:
  - What is Ownership in Move?
  - How do I use Ownership in Move?
  - What is Account Owner (or Single Owner) in Move?
  - What is Shared State in Move?
answer: 'Object ownership types in Sui: single owner, shared state, immutable objects, and object-owned objects explained with examples.'
goal:
  description: 'Reader understands object ownership types in Sui: single owner, shared state, immutable objects, and object-owned objects explained with examples'
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

# 所有權 (Ownership) {#ownership}

Sui 上的每個物件都處於五種所有權狀態之一：_單一擁有者_、_共享_、_不可變
（凍結）_、_物件擁有者_，或 _參與方_。每個模型皆具備獨特特性，適合不同的
使用案例；而且，如同我們將在[下一節](./fast-path-and-consensus)看到的，所有權的選擇也會決定如何執行涉及該物件的交易。

請參閱[儲存函式](../storage/storage-functions.md)章節，了解如何變更物件的
擁有者或所有權類型。

## 帳戶擁有者（或單一擁有者） (Account Owner (or Single Owner)) {#account-owner-or-single-owner}

帳戶擁有者，也稱為 _單一擁有者_ 模型，是 Sui 的基礎所有權類型。在此模型中，
物件由單一帳戶擁有，該帳戶可在與其類型相關的行為範圍內，對物件進行專屬控制。
此模型體現了 _真正所有權_ 的概念：只有擁有者可以在交易中使用物件——無論是讀取、
修改或將其轉移出去——其他人都無法碰觸它。相較於其他區塊鏈系統，此種明確的所有權
是一項重要優勢；在其他系統中，所有權的定義可能較為模糊，智慧合約也可能可以在未經
擁有者同意的情況下變更或轉移資產。

可以把它想成你的手機：你可以解鎖並操作它，其他人則無法做到。Sui 在系統層級強制
執行此規則——沒有任何方式可以「破解密碼」並使用屬於他人的物件，因此除非你授權，
否則沒有人可以使用你的資產。

## 共享狀態 (Shared State) {#shared-state}

單一擁有者模型有其限制。以數位資產市集為例：Alice 擁有資產 X，並希望將其上架出售，
讓 Bob 或其他任何人可以前來購買。若只有單一擁有者物件，這件事出乎意料地難以表達：
若要讓交易在 Alice 未參與的情況下完成，該資產必須放在賣方與任何未來買方皆可存取的
位置，而且不能由任何單一帳戶擁有。

為解決共享資料存取的問題，Sui 提供 _共享_ 所有權模型。共享物件屬於網路：任何帳戶
都可以讀取及修改它，而互動規則則由實作該物件的模組定義。共享物件的典型用途包括市集、
共享資源、託管，以及其他需要多個帳戶存取相同狀態的情境。

## 參與方物件 (Party Objects) {#party-objects}

最新的所有權狀態 _參與方_ 物件位於上述兩種模型之間：如同單一擁有者物件，它有一名
擁有者——使用它需要該地址的許可；但如同共享物件，涉及它的交易會由共識排序。目前，
參與方物件一律由單一地址擁有；此狀態的設計是為了最終支援更複雜的設定，讓權限可在
多個參與方之間分配。

參與方物件以專屬所有權的速度換取共識排序的彈性——適合經常由高流量服務存取的資產，
其中許多獨立且往返於同一擁有者的轉移可能會同時進行。對大多數應用程式而言，它們是
進階選項，而非起點：先從單一擁有者物件開始，並在出現明確需求時改用參與方物件。

> 此處列出參與方物件以完整呈現所有權狀態。其轉移函式請參閱
> [附錄 C：轉移函式](./../appendix/transfer-functions#party)，而
> [`sui::party`](https://docs.sui.io/references/framework/sui/party) 模組文件則涵蓋
> 詳細內容。

## 不可變（凍結）狀態 (Immutable (Frozen) State) {#immutable-frozen-state}

Sui 也提供 _凍結物件_ 模型，讓物件永久成為唯讀。這些不可變物件雖然可讀取，
但無法修改、轉移或刪除，為所有網路參與者提供穩定且固定的狀態。凍結物件很適合公開
資料、參考資料，以及其他適合保持狀態永久性的使用案例。

## 物件擁有者 (Object Owner) {#object-owner}

Sui 最後一種所有權模型是 _物件擁有者_：由另一個物件擁有的物件。此功能可建立物件
之間的複雜關係、儲存大型異質集合，以及實作可擴充且模組化的系統。由於交易是由帳戶
發起，交易會先存取父物件，再透過它取得子物件。

我們很喜歡舉遊戲角色作為使用案例。Alice 可以擁有遊戲中的 Hero 物件，而 Hero 可以
擁有物品：它們同樣以物件表示，例如「Map」或「Compass」。Alice 可以從「Hero」物件
取出「Map」，接著將它轉移給 Bob，或在市集上出售。透過物件擁有者，可以很自然地想像
資產如何彼此建立關係、組織與管理。

> 父子關係背後有兩種機制，兩者皆會在本書稍後說明：
> [動態欄位](./../programmability/dynamic-fields)及
> [轉移至物件](./../storage/transfer-to-object)。

## 總結 (Summary) {#summary}

- **單一擁有者：** 物件由單一帳戶擁有，該帳戶對物件具有專屬控制權。
- **共享狀態：** 物件可與網路共享，讓多個帳戶能夠讀取及修改物件。
- **參與方：** 物件有單一擁有者，但會透過共識進行排序——這是較新且進階的選項。
- **不可變狀態：** 物件永久成為唯讀，提供穩定且固定的狀態。
- **物件擁有者：** 物件可擁有其他物件，支援複雜關係與模組化系統。

## 後續步驟 (Next Steps) {#next-steps}

在下一節中，我們將說明 Sui 中的交易執行路徑，以及所有權模型如何影響交易執行。
