---
description: Move 中的結構方法 (Struct methods)：使用接收者語法 (receiver syntax)，透過點記法 (dot notation) 在結構執行個體 (struct instances) 上呼叫函式 (functions)，讓原始碼更簡潔。
title: 結構方法 (Struct Methods)
keywords:
  - Move
  - Sui
  - Move tutorial
  - struct
  - methods
questions:
  - What is Struct Methods in Move?
  - How do I use Struct Methods in Move?
  - What is Method Syntax in Move?
  - What is Method Aliases in Move?
answer: 'Struct methods in Move: use receiver syntax to call functions on struct instances with dot notation for cleaner code.'
goal:
  description: 'Reader understands struct methods in Move: use receiver syntax to call functions on struct instances with dot notation for cleaner code'
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

# 結構方法 (Struct Methods) {#struct-methods}

在前面的章節中，我們使用點運算子在值上呼叫函式：
`v.length()`、`opt.is_some()`、`artist.name()`。這是*接收者語法*（receiver syntax）——「接收者」是指接收方法呼叫的執行個體——本節將說明其運作方式以及如何控制它。方法能讓操作結構的程式碼讀起來更自然：值在前，操作在後，而且無須匯入或明確寫出函式所屬的模組。

## 方法語法 (Method Syntax) {#method-syntax}

核心規則是：當函式的第一個引數是與函式定義於*相同模組*中的結構時，即可使用 `.` 運算子呼叫該函式。這類方法會自動在使用該結構的任何地方可用——這正是為什麼取得 `vector` 和 `Option` 值後，便能立即以點語法呼叫它們。如果第一個引數的型別定義於另一個模組，該函式預設不會與該結建置立關聯，必須使用標準函式呼叫語法——除非如以下所示宣告了*別名*。

```move file=packages/samples/sources/move-basics/struct-methods.move anchor=hero

```

## 方法別名 (Method Aliases) {#method-aliases}

當模組定義多個結構及其方法時，方法別名有助於避免名稱衝突。它們也能為結構提供描述性更強的方法名稱。

語法如下：

```move
// 用於區域方法關聯
use fun function_path as Type.method_name;

// 匯出的別名
public use fun function_path as Type.method_name;
```

> 僅允許為定義於相同模組中的結建置立公開別名。對於定義於其他模組中的結構，仍可建立別名，但不可將其設為公開。

在以下範例中，我們修改了 `hero` 模組並新增另一個型別——`Villain`。`Hero` 和 `Villain` 都有相似的欄位名稱與方法。為避免名稱衝突，我們分別以 `hero_` 和 `villain_` 作為方法前綴。不過，使用別名後，便可在結構執行個體上呼叫這些方法，而無須加上前綴：

```move file=packages/samples/sources/move-basics/struct-methods-2.move anchor=hero_and_villain

```

在測試函式中，會直接在 `Hero` 與 `Villain` 執行個體上呼叫 `health` 方法，無須加上前綴，因為編譯器會自動將方法與各自的結建置立關聯。

> 注意：在測試函式中，`hero.health()` 呼叫的是別名方法，而不是直接存取私有的 `health` 欄位。雖然 `Hero` 與 `Villain` 結構是公開的，但其欄位仍僅限模組內存取。方法呼叫 `hero.health()` 使用了由 `public use fun hero_health as Hero.health` 定義的公開別名，以受控方式存取私有欄位。

## 外部型別方法的別名 (Aliasing a Method of an External Type) {#aliasing-a-method-of-an-external-type}

別名不限於模組本身的結構：區域（非公開）別名可以將方法名稱附加至其他模組的型別。在此，我們為標準 `String` 型別提供額外的方法名稱 `num_bytes`——這比其 `length` 函式實際計算的內容更精確：

```move file=packages/samples/sources/move-basics/struct-methods-3.move anchor=string_alias

```

別名僅存在於宣告它的模組中——這正是它不可為 `public` 的原因：該模組並不擁有 `String` 型別，因此無法為所有其他人擴充其介面。

## 延伸閱讀 (Further Reading) {#further-reading}

- Move 參考文件中的[方法語法](./../../reference/method-syntax)。
