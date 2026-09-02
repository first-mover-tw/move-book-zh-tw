---
description:
  '常數 (Constants) in Move: how to define immutable module-level values, naming conventions, and supported constant types.


  翻譯：


  Move 中的常數 (Constants)：如何定義不可變的模組層級數值、命名慣例，以及支援的常數型別。'
---

# Constants 常數 (Constants) {#constants}

常數是在模組層級定義的不可變值。它們通常用來為整個模組中使用的靜態值命名。例如，如果某個產品有預設價格，你可能會為它定義一個常數。常數儲存在模組的位元組碼中，每次使用時都會複製該值。跟每個模組成員一樣，常數預設是私有的——而且與函式或結構體不同，常數無法被設為公開；下方的 [config 模式](#using-the-config-pattern) 展示了如何在模組之間共享它們。

```move file=packages/samples/sources/move-basics/constants-shop-price.move anchor=shop_price

```

## 命名慣例 (Naming Convention) {#naming-convention}

常數必須以大寫字母開頭——這是在編譯器層級強制執行的。對於作為值使用的常數，慣例是使用全大寫字母並在單字之間加底線，這讓常數在程式碼中與其他識別字有所區別。[錯誤常數](./assert-and-abort#error-constants)是個例外，它們寫成 `E` 後接 CamelCase 描述，例如 `ENoAccess`。

```move file=packages/samples/sources/move-basics/constants-naming.move anchor=naming

```

## 常數是不可變的 (Constants Are Immutable) {#constants-are-immutable}

常數不能被更改或指派新值。作為套件位元組碼的一部分，它們本質上是不可變的。

```move
module book::immutable_constants;

const ITEM_PRICE: u64 = 100;

// 會發出錯誤
fun change_price() {
    ITEM_PRICE = 200;
}
```

## 使用 Config 模式 (Using the Config Pattern) {#using-the-config-pattern}

應用程式的常見用例是定義一組在整個程式碼庫中使用的常數。但由於常數是模組私有的，其他模組無法存取它們。解決這個問題的一種方式是定義一個「config」模組，透過公開函式匯出這些常數：

```move file=packages/samples/sources/move-basics/constants-config.move anchor=config

```

如此一來，其他模組就可以匯入並讀取這些常數，同時簡化了更新流程。如果需要變更常數，只需要在套件升級時更新 config 模組即可。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move Reference 中的[常數](./../../reference/constants)
- [常數的程式碼撰寫慣例](./../guides/code-quality-checklist#regular-constants-are-all_caps)
