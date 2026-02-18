---

description: "Constants in Move: how to define immutable module-level values, naming conventions, and supported constant types."
---

# 常數 (Constants)

常數是在模組層級定義的不可變值。它們通常用於為整個模組中使用的靜態值命名。例如，如果某個產品有預設價格，您可以為其定義一個常數。常數儲存在模組的位元組碼 (bytecode) 中，每次使用它們時，該值都會被複製。

```move file=packages/samples/sources/move-basics/constants-shop-price.move anchor=shop_price

```

## 命名規範

常數必須以大寫字母開頭 — 這是編譯器強制執行的。對於用作值的常數，慣例是使用全大寫字母並在單字之間加上底線，這使得常數在程式碼中的其他識別碼中脫穎而出。有一個例外是 [錯誤常數](./assert-and-abort#error-constants)，它們使用 **大寫前綴後接大駝峰式 (ECamelCase)** 編寫。

```move file=packages/samples/sources/move-basics/constants-naming.move anchor=naming

```

## 常數是不可變的

常數一旦定義就無法更改或指派新值。作為套件位元組碼的一部分，它們本質上就是不可變的。

```move
module book::immutable_constants;

const ITEM_PRICE: u64 = 100;

// 會產生錯誤
fun change_price() {
    ITEM_PRICE = 200;
}
```

## 使用 Config 模式

應用程式的一個常見用例是定義一組在整個程式碼庫中使用的常數。但由於常數對模組而言是私有的，因此無法從其他模組存取。解決此問題的一種方法是定義一個「config」模組來導出這些常數（透過函式）。

```move file=packages/samples/sources/move-basics/constants-config.move anchor=config

```

這樣，其他模組就可以匯入並讀取這些常數，且更新過程也變得更加簡單。如果需要更改常數，只需在套件升級期間更新 config 模組即可。

## 相關連結

- Move 參考手冊中的 [常數 (Constants)](./../../reference/constants)
- [常數編碼規範](./../guides/code-quality-checklist)
