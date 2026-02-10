# 動態物件欄位 (Dynamic Object Fields)

在上一節中，我們介紹了[動態欄位](./dynamic-fields)，它允許向物件動態添加資料。在這部分中，我們將介紹它的對應版本 —— 「動態物件欄位 (Dynamic Object Fields)」，並解釋它的特點。

## 定義

動態物件欄位定義在 `sui::dynamic_object_field` 模組中。與動態欄位類似，它們透過一個名稱附加到物件的 `UID` 上。主要區別在於動態物件欄位專門用於存儲具有 [`key`](./../storage/key-ability.md) 能力的物件。

```move
module sui::dynamic_object_field;

/// 用於存儲欄位的內部物件。
public struct Wrapper<Name: copy + drop + store> has key {
    id: UID,
    name: Name,
}
```

由於儲存在動態物件欄位中的「值 (value)」本身就是一個物件，內部的 `Wrapper` 結構不需要攜帶該值。相反地，它作為動態物件欄位的代表存在，而實際的物件則單獨存儲。

在 Sui 存儲模型中，具有 `key` 能力的物件具有與正常地址擁有的物件相同的狀態，且其擁有者是父物件的 ID。

## 用法

動態物件欄位的用法與動態欄位幾乎相同：可以使用 `add` 添加物件，使用 `remove` 移除物件，並使用 `borrow` 和 `borrow_mut` 獲取對物件的參考。

```move file=packages/samples/sources/programmability/dynamic-object-fields.move anchor=usage

```

在上述範例中，我們向 `Character` 添加了一個 `Hat` 物件。與動態欄位的主要區別在於，`Hat` 物件現在是一個獨立的物件。這反映在鏈下索引器中，因為 `Hat` 物件現在擁有 `Character` 物件的 ID 作為其擁有者地址。

## 與動態欄位的區別

動態物件欄位與動態欄位在幾個重要方面有所不同：

1. **鏈下發現**：由於存儲在動態物件欄位中的值是獨立的物件，它們可以很容易地被鏈下工具發現。
2. **刪除證明**：如果刪除了一個具有 [`key`](./../storage/key-ability.md) 能力的物件，系統會獲取刪除證明，這可以由某些鏈上應用程式利用。
3. **物件轉移**：動態物件欄位中的物件可以像其他物件一樣被轉移或操作，只要它們被模組邏輯正確獲取。

## 孤立動態物件欄位

與動態欄位一樣，如果不小心操作，動態物件欄位也可能會變得孤立。一旦父項 UID 被刪除，動態物件欄位將無法透過正常的父子關係存取。

<div class="tip">

始終建議使用正確清理動態欄位和動態物件欄位的邏輯來實作物件刪除，或使用 [動態集合](./dynamic-collections) 來幫助管理它們。

</div>

## 總結

動態物件欄位是動態欄位的強大擴展，專為存儲物件而設計。它們結合了動態欄位的靈活性與地址擁有物件的特性，使其成為 Sui 上開發複雜去中心化應用程式的必備工具。

[dynamic-fields]: ./dynamic-fields.md
