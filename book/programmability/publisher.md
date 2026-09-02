---
description: 發布者物件 (Publisher object) 在 Sui：證明套件權限，用於配置顯示 (Display)、轉移政策 (transfer policies) 以及其他型別層級設定。
---

# 發行者授權 (Publisher Authority) {#publisher-authority}

應用程式經常需要證明**是誰發行了某個型別**。這在數位資產的情境中尤其重要，因為發行者可能為其資產啟用或停用某些功能。Publisher 物件定義於 [Sui Framework](./sui-framework) 中，讓發行者能夠證明其對某型別的**授權**。

## 定義 (Definition) {#definition}

Publisher 物件定義於 Sui Framework 的 `sui::package` 模組中。它是一個非常簡單、非泛型的物件，每個模組可初始化一次（每個 package 可初始化多次），用來證明發行者對某型別的授權。若要取得 Publisher 物件，發行者必須向 `package::claim` 函式提供一個 [One Time Witness](./one-time-witness)。

```move
module sui::package;

public struct Publisher has key, store {
    id: UID,
    package: String,
    module_name: String,
}
```

以下是在模組中取得 `Publisher` 物件的簡單範例：

```move file=packages/samples/sources/programmability/publisher.move anchor=publisher

```

> 對於常見的取得後即轉移流程，`sui::package` 模組也提供了一個簡便寫法 -
> `package::claim_and_keep` - 它會在一次呼叫中取得 `Publisher` 物件並將其轉移給發送者。

## 用法 (Usage) {#usage}

Publisher 物件有兩個相關的函式 - `from_module` 和 `from_package` -
用來檢查某型別是否定義於此 `Publisher` 所代表的模組或 package 中：

```move file=packages/samples/sources/programmability/publisher.move anchor=use_publisher

```

## 作為管理員角色的 Publisher (Publisher as Admin Role) {#publisher-as-admin-role}

對於小型應用程式或簡單的使用情境，Publisher 物件可作為管理員
[capability](./capability) 使用。雖然在更廣泛的情境中，Publisher 物件掌控著
系統設定，但它也能用來管理應用程式的狀態。

```move file=packages/samples/sources/programmability/publisher.move anchor=publisher_as_admin

```

然而，Publisher 物件缺乏
[Capabilities](./capability) 的一些原生特性，例如型別安全性與表達力。
`admin_action` 的簽章完全沒有說明所需的授權 - 任何持有*任何* `Publisher` 物件的人
都可以呼叫此函式，因此授權檢查必須在函式主體內進行。
而且由於每個已發行的 package 都會產生一個 `Publisher`，若忘記進行 `from_module` 檢查，
將會使該動作對網路上的每個發行者開放。基於這些原因，在
使用 `Publisher` 物件作為管理員角色時務必謹慎。

## 在 Sui 上的角色 (Role on Sui) {#role-on-sui}

某些 Sui 上的功能需要 Publisher。[Object Display](./display) 可以在
定義該型別的模組之外，使用 Publisher 來建立，而 TransferPolicy - Kiosk 系統的
重要元件 - 也需要 Publisher 物件來證明對該型別的擁有權。

## 下一步 (Next Steps) {#next-steps}

在下一節中，我們將介紹第一個可以使用 Publisher 物件的功能 - Object
Display - 一種向客戶端描述物件、並將元資料標準化的方式。這是打造
使用者友善應用程式時不可或缺的一環。
