# 結構體 (Structs)

結構體是 Move 中定義自定義數據類型的唯一方式。結構體可以包含多種不同類型的欄位。

## 定義結構體

使用 `public struct` 關鍵字來定義一個新的結構體。

```move
public struct Foo has copy, drop {
    x: u64,
    y: bool
}

// 位置結構體 (Positional struct)
public struct Bar(u64, bool) has copy, drop;
```

## 能力 (Abilities)

結構體可以具有四種能力：`copy`, `drop`, `store`, 和 `key`。能力控制著結構體值的行為（例如是否可以複製或捨棄）。

## 欄位操作

### 借用欄位

您可以使用 `.` 運算符與 `&` 或 `&mut` 來借用結構體的欄位。

```move
let foo = Foo { x: 3, y: true };
let x_ref = &foo.x;
```

### 讀取與寫入欄位

如果類型具有 `copy` 能力，可以直接讀取欄位。如果類型具有 `drop` 能力，可以直接修改欄位。

```move
let mut foo = Foo { x: 3, y: true };
foo.x = 42;
let x = foo.x;
```

## 特權操作 (Privileged Operations)

結構體的大多數操作只能在宣告它的模組內部執行：
- 建立 (Pack) 和 銷毀 (Unpack)。
- 訪問欄位。

這使得開發者可以定義嚴格的封裝和不變量。

## 所有權 (Ownership)

預設情況下，結構體是線性的，這意味著它們既不能被複製也不能被捨棄。這在模擬貨幣等真實世界資產時非常有用。要銷毀一個沒有 `drop` 能力的結構體，必須在模組內手動解構它。

## 存儲 (Storage)

結構體可以用於定義存儲模式。具有 `key` 能力的結構體可以作為物件存儲在鏈上。
