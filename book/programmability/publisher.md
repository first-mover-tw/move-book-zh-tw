---

description: "The Publisher object in Sui: prove package authority to configure Display, transfer policies, and other type-level settings."
---

# 發佈者權限 (Publisher Authority)

在應用程式設計與開發中，通常需要證明發佈者權限。這在數位資產的背景下尤為重要，發佈者可能需要為其資產啟用或停用某些功能。發佈者物件 (Publisher Object) 是在 [Sui 框架](./sui-framework) 中定義的一種物件，它允許發佈者證明其對於 **某種類型的權限 (authority over a type)**。

## 定義

發佈者物件定義在 Sui 框架的 `sui::package` 模組中。它是一個非常簡單、非泛型的物件，每個模組只能初始化一次（每個套件可以有多個），用於證明發佈者對某種類型的權限。要領取發佈者物件，發佈者必須向 `package::claim` 函式提供 [一次性見證 (One Time Witness, OTW)](./one-time-witness)。

```move
module sui::package;

public struct Publisher has key, store {
    id: UID,
    package: String,
    module_name: String,
}
```

> 如果您不熟悉一次性見證，可以在 [這裡](./one-time-witness) 閱讀更多相關資訊。

以下是在模組中領取 `Publisher` 物件的簡單範例：

```move file=packages/samples/sources/programmability/publisher.move anchor=publisher

```

## 用法

發佈者物件有兩個相關聯的函式，用於證明發佈者對某種類型的權限：

```move file=packages/samples/sources/programmability/publisher.move anchor=use_publisher

```

## 發佈者作為管理員角色 (Publisher as Admin Role)

對於小型應用程式或簡單的使用案例，發佈者物件可以用作管理員 [能力 (Capability)](./capability)。雖然在更廣泛的背景下，發佈者物件控制著系統配置，但它也可以用來管理應用程式的狀態。

```move file=packages/samples/sources/programmability/publisher.move anchor=publisher_as_admin

```

然而，發佈者缺少 [能力 (Capability)](./capability) 的某些原生特性，例如類型安全和表現力。`admin_action` 的簽名並非十分明確，任何人都可以呼叫。而且由於 `Publisher` 物件是標準化的，如果不執行 `from_module` 檢查，就會存在未經授權存取的風險。因此，將 `Publisher` 物件用作管理員角色時必須謹慎。

## 在 Sui 上的角色

Sui 上的某些功能需要發佈者物件。[物件顯示 (Object Display)](./display) 只能由發佈者建立，而 TransferPolicy —— Kiosk 系統中的一個重要組件 —— 也需要發佈者物件來證明類型的所有權。

## 下一步

在下一章中，我們將介紹第一個需要發佈者物件的功能：物件顯示 (Object Display) —— 一種為客戶端描述物件並標準化元資料的方法。這是構建使用者友善應用程式的必備功能。
