---
title: 索引語法 (Index Syntax) | 參考手冊
description: 'Move 索引語法 (index syntax) 參考資料：使用方括號標記法 (bracket notation)，針對具有 #[syntax(index)] 屬性的自訂型別 (custom types)，實現直覺的存取模式 (access patterns)。'
keywords:
  - Move
  - Sui
  - Move reference
  - index
  - syntax
  - reference
questions:
  - How does Index Syntax work in Move?
  - What is the syntax for Index Syntax in Move?
  - What is Usage in Move?
  - What is Defining Index Syntax Functions in Move?
answer: 'Move index syntax reference: use bracket notation for custom types with #[syntax(index)] attribute for intuitive access patterns.'
goal:
  description: 'Reader understands move index syntax reference: use bracket notation for custom types with #[syntax(index)] attribute for intuitive access patterns'
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

# 索引語法 (Index Syntax) {#index-syntax}

Move 提供語法屬性，讓你可以定義外觀與使用方式如同原生 Move 原始碼的操作，並將這些操作降低為你提供的定義。

我們的第一個語法方法 `index`，讓你可以透過為應用於這些索引操作的函式加上註記，定義一組可作為資料型別自訂索引存取子的操作，例如以 `m[i,j]` 存取矩陣元素。此外，這些定義會針對各個型別量身訂做，且任何使用你型別的程式設計師都能隱含使用。

## 概觀與總結 (Overview and Summary) {#overview-and-summary}

首先，考慮一個使用向量的向量來表示其值的 `Matrix` 型別。你可以透過在 `borrow` 與 `borrow_mut` 函式上使用 `index` 語法註記，撰寫一個小型函式庫，如下所示：

```move
module matrix::matrix;

public struct Matrix<T> { v: vector<vector<T>> }

#[syntax(index)]
public fun borrow<T>(s: &Matrix<T>, i: u64, j: u64): &T {
    vector::borrow(vector::borrow(&s.v, i), j)
}

#[syntax(index)]
public fun borrow_mut<T>(s: &mut Matrix<T>, i: u64, j: u64): &mut T {
    vector::borrow_mut(vector::borrow_mut(&mut s.v, i), j)
}

public fun make_matrix<T>(v: vector<vector<T>>):  Matrix<T> {
    Matrix { v }
}
```

現在，任何使用此 `Matrix` 型別的人都可使用其索引語法：

```move
let mut m = matrix::make_matrix(vector[
    vector[1, 0, 0],
    vector[0, 1, 0],
    vector[0, 0, 1],
]);x

let mut i = 0;
while (i < 3) {
    let mut j = 0;
    while (j < 3) {
        if (i == j) {
            assert!(m[i, j] == 1, 1);
        } else {
            assert!(m[i, j] == 0, 0);
        };
        *(&mut m[i,j]) = 2;
        j = j + 1;
    };
    i = i + 1;
}
```

## 使用方式 (Usage) {#usage}

如範例所示，如果你定義資料型別及其關聯的索引語法方法，任何人都可以藉由在該型別的值上撰寫索引語法來呼叫該方法：

```move
let mat = matrix::make_matrix(...);
let m_0_0 = mat[0, 0];
```

在編譯期間，編譯器會根據運算式的位置與可變使用方式，將其轉譯為適當的函式呼叫：

```move
let mut mat = matrix::make_matrix(...);

let m_0_0 = mat[0, 0];
// 轉譯為 `copy matrix::borrow(&mat, 0, 0)`

let m_0_0 = &mat[0, 0];
// 轉譯為 `matrix::borrow(&mat, 0, 0)`

let m_0_0 = &mut mat[0, 0];
// 轉譯為 `matrix::borrow_mut(&mut mat, 0, 0)`
```

你也可以將索引運算式與欄位存取交錯使用：

```move
public struct V { v: vector<u64> }

public struct Vs { vs: vector<V> }

fun borrow_first(input: &Vs): &u64 {
    &input.vs[0].v[0]
    // 轉譯為 `vector::borrow(&vector::borrow(&input.vs, 0).v, 0)`
}
```

### 索引函式可接受彈性的引數 (Index Functions Take Flexible Arguments) {#index-functions-take-flexible-arguments}

請注意，除了本章其餘部分所述的定義與型別限制外，Move 對你的索引語法方法可接受作為參數的值沒有任何限制。這讓你能在定義索引語法時實作複雜的程式化行為，例如當索引超出範圍時使用預設值的資料結構：

```move
#[syntax(index)]
public fun borrow_or_set<Key: copy, Value: drop>(
    input: &mut MTable<Key, Value>,
    key: Key,
    default: Value
): &mut Value {
    if (contains(input, key)) {
        borrow(input, key)
    } else {
        insert(input, key, default);
        borrow(input, key)
    }
}
```

現在，當你索引 `MTable` 時，也必須提供預設值：

```move
let string_key: String = ...;
let mut table: MTable<String, u64> = m_table::make_table();
let entry: &mut u64 = &mut table[string_key, 0];
```

這類可擴充的能力讓你能為型別撰寫精確的索引介面，明確強制實施量身打造的行為。

## 定義索引語法函式 (Defining Index Syntax Functions) {#defining-index-syntax-functions}

這種強大的語法形式可讓所有你自訂的資料型別以此方式運作，前提是你的定義符合下列規則：

1. 在與目標型別相同的模組中，於指定函式加上 `#[syntax(index)]` 屬性。
1. 指定函式具有 `public` 可見性。
1. 函式以參考型別作為其目標型別（第一個引數），並回傳相符的參考型別（若目標為 `mut`，則回傳 `mut`）。
1. 每個型別只能有一個可變定義與一個不可變定義。
1. 不可變與可變版本必須在型別上相符：
   - 目標型別相符，僅可變性不同。
   - 回傳型別需符合其目標型別的可變性。
   - 若有型別參數，兩個版本的約束必須完全相同。
   - 除目標型別外的所有參數必須完全相同。

以下內容與額外範例會更詳細地說明這些規則。

### 宣告 (Declaration) {#declaration}

若要宣告索引語法方法，請在目標型別定義所在的相同模組中，於相關函式定義上方加入 `#[syntax(index)]` 屬性。這會向編譯器表示該函式是指定型別的索引存取子。

#### 不可變存取子 (Immutable Accessor) {#immutable-accessor}

不可變索引語法方法是為唯讀存取而定義。它接受目標型別的不可變參考，並回傳元素型別的不可變參考。`std::vector` 中定義的 `borrow` 函式即為範例：

```move
#[syntax(index)]
public native fun borrow<Element>(v: &vector<Element>, i: u64): &Element;
```

#### 可變存取子 (Mutable Accessor) {#mutable-accessor}

可變索引語法方法是不可變版本的對應方法，可同時進行讀取與寫入操作。它接受目標型別的可變參考，並回傳元素型別的可變參考。`std::vector` 中定義的 `borrow_mut` 函式即為範例：

```move
#[syntax(index)]
public native fun borrow_mut<Element>(v: &mut vector<Element>, i: u64): &mut Element;
```

#### 可見性 (Visibility) {#visibility}

為確保可在型別使用的任何位置使用索引函式，所有索引語法方法都必須具有 public 可見性。這可確保在 Move 的模組與套件間以便利方式使用索引功能。

#### 不可重複 (No Duplicates) {#no-duplicates}

除了上述要求外，我們限制每個目標基礎型別只能為不可變參考定義一個索引語法方法，並為可變參考定義一個索引語法方法。例如，你無法為多型型別定義特化版本：

```move
#[syntax(index)]
public fun borrow_matrix_u64(s: &Matrix<u64>, i: u64, j: u64): &u64 { ... }

#[syntax(index)]
public fun borrow_matrix<T>(s: &Matrix<T>, i: u64, j: u64): &T { ... }
    // 錯誤！Matrix 已經定義了
    // 其不可變索引語法方法
```

這可確保你永遠能判斷呼叫的是哪個方法，而無須檢查型別具現化。

### 型別約束 (Type Constraints) {#type-constraints}

預設情況下，索引語法方法具有下列型別約束：

**其目標型別（第一個引數）必須是對單一型別的參考，且該型別定義於與標記函式相同的模組中。** 這表示你無法為 tuple、型別參數或值定義索引語法方法：

```move
#[syntax(index)]
public fun borrow_fst(x: &(u64, u64), ...): &u64 { ... }
    // 因為目標型別是 tuple，所以發生錯誤

#[syntax(index)]
public fun borrow_tyarg<T>(x: &T, ...): &T { ... }
    // 因為目標型別是型別參數，所以發生錯誤

#[syntax(index)]
public fun borrow_value(x: Matrix<u64>, ...): &u64 { ... }
    // 因為 x 不是參考，所以發生錯誤
```

**目標型別必須與回傳型別具有相同的可變性。** 此限制可讓你在將已索引運算式借用為 `&vec[i]` 或 `&mut vec[i]` 時，明確表達預期行為。Move 編譯器會使用可變性標記來決定要呼叫哪種借用形式，以產生具有適當可變性的參考。因此，我們不允許目標與回傳可變性不同的索引語法方法：

```move
#[syntax(index)]
public fun borrow_imm(x: &mut Matrix<u64>, ...): &u64 { ... }
    // 錯誤！可變性不相容
    // 預期回傳可變參考型別 '&mut'
```

### 型別相容性 (Type Compatibility) {#type-compatibility}

定義一組不可變與可變索引語法方法時，它們必須符合多項相容性約束：

1. 必須接受相同數量的型別參數，且這些型別參數必須具有相同的約束。
1. 型別參數必須依據其 _位置_ 而非名稱以相同方式使用。
1. 除可變性外，其目標型別必須完全相符。
1. 除可變性外，其回傳型別必須完全相符。
1. 所有其他參數型別必須完全相符。

這些約束旨在確保索引語法無論位於可變或不可變位置時，行為都完全一致。

為說明其中一些錯誤，請回想先前的 `Matrix` 定義：

```move
#[syntax(index)]
public fun borrow<T>(s: &Matrix<T>, i: u64, j: u64): &T {
    vector::borrow(vector::borrow(&s.v, i), j)
}
```

下列所有定義都與可變版本的型別不相容：

```move
#[syntax(index)]
public fun borrow_mut<T: drop>(s: &mut Matrix<T>, i: u64, j: u64): &mut T { ... }
    // 錯誤！此處的 `T` 具有 `drop`，但不可變版本中沒有

#[syntax(index)]
public fun borrow_mut(s: &mut Matrix<u64>, i: u64, j: u64): &mut u64 { ... }
    // 錯誤！這接受不同數量的型別參數

#[syntax(index)]
public fun borrow_mut<T, U>(s: &mut Matrix<U>, i: u64, j: u64): &mut U { ... }
    // 錯誤！這接受不同數量的型別參數

#[syntax(index)]
public fun borrow_mut<U>(s: &mut Matrix<U>, i_j: (u64, u64)): &mut U { ... }
    // 錯誤！這接受不同數量的引數

#[syntax(index)]
public fun borrow_mut<U>(s: &mut Matrix<U>, i: u64, j: u32): &mut U { ... }
    // 錯誤！`j` 是不同的型別
```

再次強調，此處的目標是讓不可變與可變版本的使用方式保持一致。這讓索引語法方法可在不依據可變或不可變使用方式改變行為或約束的情況下運作，最終確保可供程式設計使用的一致介面。
