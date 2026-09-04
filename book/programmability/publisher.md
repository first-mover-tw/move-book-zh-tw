---
description: Sui 中的發佈者物件 (Publisher object)：證明套件權限 (package authority)，以設定顯示 (Display)、轉移政策 (transfer policies) 與其他型別層級設定 (type-level settings)。
title: 發佈者權限 (Publisher Authority)
keywords:
  - Move
  - Sui
  - Move tutorial
  - publisher
  - authority
  - package
questions:
  - What is Publisher Authority in Move?
  - How do I use Publisher Authority in Move?
  - What is Definition in Move?
  - What is Usage in Move?
answer: 'The Publisher object in Sui: prove package authority to configure Display, transfer policies, and other type-level settings.'
goal:
  description: 'Reader understands the Publisher object in Sui: prove package authority to configure Display, transfer policies, and other type-level settings'
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

# 發布者權限 (Publisher Authority) {#publisher-authority}

應用程式通常需要證明 _誰發布了某個型別_。這在數位資產的情境中尤其重要，因為發布者可能會為其資產啟用或停用特定功能。[Sui Framework](./sui-framework) 中定義的 Publisher 物件，可讓發布者證明其 _對某個型別的權限_。

## 定義 (Definition) {#definition}

Publisher 物件定義於 Sui Framework 的 `sui::package` 模組中。它是一個非常簡單的非泛型物件，每個模組可初始化一次（每個套件則可初始化多次），用於證明發布者對某個型別的權限。若要領取 Publisher 物件，發布者必須向 `package::claim` 函式提供[一次性見證](./one-time-witness)。

```move
module sui::package;

public struct Publisher has key, store {
    id: UID,
    package: String,
    module_name: String,
}
```

以下是在模組中領取 `Publisher` 物件的簡單範例：

```move file=packages/samples/sources/programmability/publisher.move anchor=publisher

```

> 對於常見的領取並轉移流程，`sui::package` 模組也提供了簡寫形式：
> `package::claim_and_keep`，可在一次呼叫中領取 `Publisher` 物件並將其轉移給傳送者。

## 用法 (Usage) {#usage}

Publisher 物件具有兩個相關函式：`from_module` 與 `from_package`。它們會檢查某個型別是否定義於此 `Publisher` 所代表的模組或套件中：

```move file=packages/samples/sources/programmability/publisher.move anchor=use_publisher

```

## 發布者作為管理員角色 (Publisher as Admin Role) {#publisher-as-admin-role}

對於小型應用程式或簡單的使用情境，Publisher 物件可作為管理員[權能](./capability)使用。雖然在更廣泛的情境中，Publisher 物件可控制系統設定，它也可用於管理應用程式的狀態。

```move file=packages/samples/sources/programmability/publisher.move anchor=publisher_as_admin

```

不過，Publisher 物件缺乏[權能](./capability)的一些原生特性，例如型別安全性與表達能力。`admin_action` 的簽章未說明所需的權限；任何持有 _任何_ `Publisher` 物件的人都可以呼叫此函式，因此必須在函式主體內檢查授權。而且，由於每個已發布的套件都會產生一個 `Publisher`，若忘記進行 `from_module` 檢查，網路上的每位發布者都能執行該動作。因此，將 `Publisher` 物件作為管理員角色時，務必謹慎。

## Sui 上的角色 (Role on Sui) {#role-on-sui}

Sui 的特定功能需要 Publisher。[物件顯示](./display)在定義型別的模組外設定時，可使用 Publisher 建立；而 Kiosk 系統的重要元件 TransferPolicy 也需要 Publisher 物件來證明該型別的所有權。

## 後續步驟 (Next Steps) {#next-steps}

下一節將介紹第一項可使用 Publisher 物件的功能：物件顯示。它提供一種向用戶端描述物件並標準化中繼資料的方法，是打造使用者友善應用程式不可或缺的功能。
