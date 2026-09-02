---
description: 在 Sui Move 中處理餘額 (Balance)、代幣 (Coin) 與代幣註冊表 (CoinRegistry)：使用 Currency 標準建立同質化代幣、以 TreasuryCap 管理供應量，並將中繼資料儲存在鏈上。
---

# 餘額與 Coin (Balance and Coin) {#balance-and-coin}

同質化代幣（Fungible tokens）是最常見的數位資產：彼此可互換的價值單位，就像貨幣一樣。在 Sui 上，同質化代幣的主要抽象是
[`Coin`](https://docs.sui.io/references/framework/sui_sui/coin) - 這是錢包持有、交易接受作為輸入、以及應用程式接受作為付款的物件。擁有「10 SUI」代表擁有一個
值為 10 SUI 的 `Coin<SUI>` 物件。

有兩個輔助型別完善了這個標準 - 一個在 `Coin` 之下，一個在其之上：

- [`Balance`](https://docs.sui.io/references/framework/sui_sui/balance) - `Coin` 內部的原始金額：一個沒有物件 ID 的純值，應用程式用它來儲存與累積資金；
- [`Currency`](https://docs.sui.io/references/framework/sui_sui/coin_registry) - 一個描述 coin 型別本身的共享物件：其元資料、供應量與監管狀態。

本節將逐一介紹這三者，並展示如何使用
`sui::coin_registry` 模組建立一種貨幣 - 這是實現此目的的標準做法。

## Balance 餘額 (Balance) {#balance}

`Balance<T>` 型別定義在 `sui::balance` 模組中。它是一個具備 `store` 能力的純值——不是物件：它沒有 `UID`，也沒有自己的儲存開銷。這使它成為_保存_資金的首選型別：每當應用程式需要在自己的型別內儲存或累積價值時——例如金庫、流動性池、託管帳戶——它會內嵌一個 `Balance`，而不是 `Coin`。

```move
/// 可儲存的餘額 - Coin 型別的內部 struct。
/// 可用來儲存不需要 key ability 的 coin。
public struct Balance<phantom T> has store {
    value: u64,
}
```

[phantom 型別參數](./../move-basics/generics#phantom-type-parameters) `T` 是使一個 balance 有別於另一個的關鍵：`Balance<GOLD>` 與 `Balance<DBL>` 是不同、不可互換的型別，即使兩者都只是儲存一個 `u64`。

`Balance` 沒有 `copy`、沒有 `drop`，也沒有公開的建構子可用於非零值。balance 只能透過增加 `T` 的總供給量來建立，也只能透過減少總供給量來消失。介於兩者之間的一切——分割、合併、儲存——只是在移動這個值。這正是套用在金錢上的[所有權](./../move-basics/ownership-and-scope)保證：不可複製、不可意外遺失。

```move file=packages/samples/sources/programmability/balance-and-coin.move anchor=balance

```

## Coin 硬幣 (Coin) {#coin}

`Balance` 無法單獨存在於儲存空間中——它必須被包裝在一個物件裡。`sui::coin::Coin` 型別就是標準的包裝器：

```move
/// 型別為 `T`、價值為 `value` 的 coin。
public struct Coin<phantom T> has key, store {
    id: UID,
    balance: Balance<T>,
}
```

具備 `key` 與 `store` 能力後，`Coin` 就是一個功能完整的物件：它可以被帳戶擁有、被轉移，也可以作為輸入被傳入交易中。用來支付交易 gas 的物件就是一個 `Coin<SUI>`。這也構成了此標準的經驗法則：邊界用 `Coin`，內部用 `Balance`。資金以 `Coin` 的形式進入應用程式，以 `Balance` 的形式儲存與累積,再以 `Coin` 的形式離開。

其 API 與 `Balance` 相似——可以拆分、合併，並在兩者之間轉換：

```move file=packages/samples/sources/programmability/balance-and-coin.move anchor=coin

```

> 以上範例使用僅供測試用的 `coin::mint_for_testing` 與 `balance::create_for_testing` 函式,憑空生成它們的 `Coin` 與 `Balance`——這是測試涉及硬幣處理程式碼的標準工具，詳見
> [在測試中使用系統物件 (Using System Objects in Tests)](./../testing/using-system-objects)。

在交易中,硬幣會受到特殊處理：原生的 `SplitCoins` 與 `MergeCoins`
[命令](./../concepts/what-is-a-transaction#commands) 會直接對硬幣進行操作，因此錢包可以準備精確的付款金額——甚至可以從 gas 硬幣中拆分出來——而無需呼叫任何模組函式。這也是為什麼模組很少需要自行公開拆分或合併功能的原因。

`sui::coin` 模組還提供了 `coin::take` 與 `coin::put` 輔助函式，它們結合了轉換與拆分/合併的步驟：`take` 會從 `Balance` 中拆分出一個 `Coin`,而 `put` 則會將一個 `Coin` 合併進 `Balance` 中。當應用程式將資金以 `Balance` 的形式儲存,並以 `Coin` 的形式送出時，這兩個函式就非常實用。

> 硬幣物件並非持有可替代價值的唯一方式：一種較新的機制可以將其直接保存在
> 某個地址上,以執行中的總額形式呈現，不需要管理任何物件。它建立在這裡所描述的型別之上，
> 詳見 [地址餘額 (Address Balances)](./address-balances) 章節。

## 貨幣與 Coin Registry (Currency and the Coin Registry) {#currency-and-the-coin-registry}

單一的 `Coin<T>` 完全沒有透露代幣 `T` 本身的任何資訊：它的名稱、符號、使用幾位小數，或其供應量如何管理。這些資訊每個型別只會儲存一次，存放在 `Currency<T>` 物件中，而所有貨幣都由 `CoinRegistry` 追蹤——這是一個具有保留地址 `0xc` 的系統物件：

```move
/// 位於地址 `0xc` 的系統物件，儲存所有已註冊
/// coin 型別的 coin 資料。
public struct CoinRegistry has key { id: UID }
```

`Currency<T>` 物件保存了關於代幣型別 `T` 的一切資訊：

```move
/// Currency 儲存 metadata，例如 name、symbol、decimals、icon_url 與
/// description，以及 supply state（選填）與法規狀態。
public struct Currency<phantom T> has key {
    id: UID,
    /// coin 用於顯示的小數位數。
    decimals: u8,
    /// coin 的人類可讀名稱。
    name: String,
    /// coin 的簡短 symbol/ticker。
    symbol: String,
    /// coin 的詳細 description。
    description: String,
    /// coin 的 icon/logo 的 URL。
    icon_url: String,
    /// coin 目前的 supply state（fixed、burn-only 或 unknown）。
    supply: Option<SupplyState<T>>,
    /// coin 的法規狀態（regulated with deny cap 或 unknown）。
    regulated: RegulatedState,
    /// 此 coin 型別的 treasury cap 的 ID（如已註冊）。
    treasury_cap_id: Option<ID>,
    /// 此 coin 型別的 metadata capability 的 ID（如已 claim）。
    metadata_cap_id: MetadataCapState,
    /// 供擴充用的額外欄位。
    extra_fields: VecMap<String, ExtraField>,
}
```

這些欄位大多都在本頁有各自獨立的章節：供應狀態（supply state）、監管狀態（regulatory status），以及兩個能力（capability）都會在下方涵蓋。不過有一個欄位值得馬上關注：
`decimals`。Move 沒有小數——`Coin` 的值是一個純整數，計算的是該貨幣的最小單位，而
`decimals` 會告訴用戶端小數點該放在哪裡以*供顯示用*。當 `decimals = 8` 時，一個
值為 `100_000_000` 的 `Coin` 會顯示為 `1` 枚代幣；原生的 SUI 貨幣有 9 位小數，其基本單位甚至有自己的名字——MIST。Move 程式碼中的金額——鑄造、拆分、比較——一律以基本單位表示。

`coin_registry` 模組是建立貨幣的*唯一*方式：它取代了原本的
`coin::create_currency` 函式，後者將中繼資料儲存在獨立的
`CoinMetadata` 物件中（我們會在[本章節末尾](#legacy-coin-metadata)涵蓋兩者的差異）。它提供了兩種建立貨幣的方式，兩者都會產生相同的結果：一個共享的 `Currency<T>` 物件，帶有一個
[衍生地址](https://docs.sui.io/references/framework/sui_sui/derived_object)，因此任何代幣型別的中繼資料都能被找到，而不需要知道其物件 ID。

### 在 `init` 中建立貨幣 (Creating a Currency in `init`) {#creating-a-currency-in-init}

最常見的流程使用[一次性見證 (One-Time Witness)](./one-time-witness)來保證某個型別的貨幣只能被建立一次，且是在[模組初始化器](./module-initializer)中：

```move file=packages/samples/sources/programmability/balance-and-coin-2.move anchor=gold

```

`new_currency_with_otw` 呼叫會回傳兩個值：

- `CurrencyInitializer` - 一個暫時性的值，用於在貨幣發布之前設定它。
  它不能被儲存或丟棄，所以在被 `finalize` 呼叫消耗之前，交易無法成功
  （這項技巧我們會在
  [Hot Potato 模式](./hot-potato-pattern)章節中探討）；
- `TreasuryCap<T>` - 控制鑄造與銷毀的[能力 (capability)](./capability)，會在下方的
  [供應量與 TreasuryCap](#supply-and-treasurycap)章節中探討。

`finalize` 呼叫還會多回傳一個能力——`MetadataCap<T>`，它控制對貨幣中繼資料的更新。然而，在 OTW 流程中，`finalize` 並不會完成註冊。
因為 `init` 是在發布過程中執行的，早於 `CoinRegistry` 能被當作參數傳入之前，`Currency<GOLD>` 物件會走一條迂迴路徑：`finalize` 會將它轉移到註冊表的地址，
在那裡等待第二個、收尾的步驟——`finalize_registration`：

```move
/// coin metadata 的「otw」初始化的第二步，接收
/// 從 init 轉移過來的 `Currency<T>`，並將其轉換成
/// 「derived address」共享物件。
///
/// 任何人皆可執行。
public fun finalize_registration<T>(
    registry: &mut CoinRegistry,
    currency: Receiving<Currency<T>>,
    _ctx: &mut TxContext,
);
```

這個函式[接收](./../storage/transfer-to-object)被送到註冊表的 `Currency<T>`，
並將它重新建立為一個具有衍生地址的共享物件。在它被呼叫之前，註冊
是不完整的：`Currency<GOLD>` 並未被共享，無法在其衍生地址找到，也
無法傳入任何讀取或更新它的函式。這個呼叫是無需權限的——任何人
都可以進行呼叫，索引器也經常這麼做——但不應該將它交由運氣決定：

> 請將 `finalize_registration` 視為 OTW 流程中強制性的一部分，而不是可有可無的清理工作。發布者應該在發布之後緊接著的交易中呼叫它——只有這樣，貨幣才算完全註冊並可供使用。

### 動態建立貨幣 (Creating a Currency Dynamically) {#creating-a-currency-dynamically}

第二種流程不需要 OTW，可以在套件發布之後的任何時間執行——例如，
在一個依需求建立貨幣的應用程式中。
`new_currency` 函式會直接接收 `CoinRegistry`，而 `Currency<T>` 會在 `finalize` 時立刻被共享，
不需要額外的註冊步驟：

```move file=packages/samples/sources/programmability/balance-and-coin-3.move anchor=doubloon

```

### 一種型別，兩種形態 (One Type, Two Shapes) {#one-type-two-shapes}

兩種流程都用一個標記型別 `T` 來為貨幣命名，但它們對這個型別
要求不同的形態，這對應了每種流程各自證明貨幣只被建立一次的方式：

- `new_currency_with_otw` 接收一個具有 `drop` 的 `T`——具體來說，是一個
  [一次性見證](./one-time-witness)：一個只有 `drop`、沒有欄位的結構，以其
  模組命名。證明就是見證*值*本身：它恰好只存在一次，會被
  該次呼叫消耗掉，並且永遠無法再次產生——因此貨幣也無法再被建立。
- `new_currency` 接收一個*僅具 key* 的 `T`——只有 `has key`，沒有其他能力，僅有單一的 `id: UID`
  欄位。這裡沒有傳入 `T` 的實例，只有型別參數，所以沒有見證值
  可以證明任何事。取而代之的是兩項檢查：`new_currency` 受
  [內部約束](./../storage/internal-constraint)所限制——就像 `sui::event::emit` 一樣，它只能
  在呼叫模組中定義的型別上被呼叫——而且如果 `Currency<T>` 已經
  被註冊過，註冊表就會中止。

僅具 key 的型別不能有 `drop`，所以同一個型別永遠無法同時用於這兩種流程。

## Supply 與 TreasuryCap (Supply and TreasuryCap) {#supply-and-treasurycap}

[Balance](#balance) 一節提到，價值只能透過增加 `T` 的總供給量來創造，也只能透過減少總供給量來消失。同時做這兩件事的型別是 `Supply<T>`，定義於 `sui::balance`，作為 `Balance` 的記帳對應物：

```move
module sui::balance;

/// T 的 Supply。用於 mint 與 burn。
public struct Supply<phantom T> has store {
    value: u64,
}

/// 以 `value` 增加 supply，建立一個新的 `Balance<T>`。
public fun increase_supply<T>(self: &mut Supply<T>, value: u64): Balance<T>;

/// 銷毀一個 `Balance<T>`，以其值減少 supply。
public fun decrease_supply<T>(self: &mut Supply<T>, balance: Balance<T>): u64;
```

這兩個函式是價值進出流通的唯一閘門，因此每一單位存在的 `Balance<T>` 都被 `Supply<T>` 記錄在案——供給量的數字永遠等於所有 `T` 餘額的總和。

正如 `Coin` 是 `Balance` 的物件形式，`TreasuryCap<T>`（由兩種建立流程回傳的能力）則是 `Supply` 的物件形式：

```move
module sui::coin;

/// 允許持有者 mint 與 burn
/// `T` 型別 coin 的 capability。可轉移
public struct TreasuryCap<phantom T> has key, store {
    id: UID,
    total_supply: Supply<T>,
}
```

擁有 `TreasuryCap` 就是擁有供給權限。它的 `mint` 與 `burn` 函式只是對供給的薄層包裝：`mint` 增加供給並將新的 `Balance` 包裝成 `Coin`，`burn` 解開一個 `Coin` 並依其值減少供給。只要 `TreasuryCap` 存在，就能用 `total_supply` 讀取目前的總量。

```move file=packages/samples/sources/programmability/balance-and-coin-3.move anchor=mint_burn

```

誰擁有 `TreasuryCap` 就控制供給，因此這個能力最終放在哪裡是一個設計決策：留給發布者做受管理的供給、儲存在應用程式物件內做程式化鑄造，或是完全放棄——如下所述。

> `Supply` 也可以獨立存在：`balance::create_supply` 會將一個 witness 轉換成原始的 `Supply<T>`——事實上，這正是我們用來介紹 [Witness 模式](./witness-pattern) 的範例——而 `treasury_into_supply` 則會從 `TreasuryCap` 中取出供給。這些都是低階工具：透過 registry 建立的貨幣應保持其 `TreasuryCap` 完整無缺，因為接下來所描述的供給狀態都是基於該能力運作的。

## 供應狀態 (Supply States) {#supply-states}

預設情況下，貨幣的供應是有彈性的 —— `Currency<T>` 物件將其記錄為 `Unknown`，
而 `TreasuryCap` 可以自由地增發與銷毀。此登錄機制支援兩種不可逆的轉換，
兩者都會消耗 `TreasuryCap`：

- `make_supply_fixed` —— 供應量從此不能再改變。上面的 `Doubloon` 範例就是使用這個方式：
  它在同一次呼叫中預先增發全部供應量並將其固定；
- `make_supply_burn_only` —— 不能再增發，但任何人都可以透過
  `coin_registry::burn` 與 `burn_balance` 函式銷毀代幣，這些函式接受共享的 `Currency` 物件並
  永久減少供應量。

這兩者都可以在初始化期間（於 `CurrencyInitializer` 上）套用，或是之後在
共享的 `Currency<T>` 物件上套用。消耗此能力（capability）不僅僅是形式上的儀式：這個轉換會拆解
`TreasuryCap` 並將其 `Supply<T>` 移入 `Currency` 物件中 —— 這也是為什麼從
這個時間點開始，`Currency` 本身會追蹤總供應量，可透過 `total_supply` 在鏈上讀取。

## 管理中繼資料 (Managing Metadata) {#managing-metadata}

貨幣的名稱、符號、描述與圖示 URL 可以在建立後透過 `set_name`、`set_symbol`、`set_description` 與 `set_icon_url` 函式更新——每個都需要一個 `MetadataCap<T>` 的參考。就像 `TreasuryCap` 一樣，`MetadataCap` 可以用 `delete_metadata_cap` 刪除，讓中繼資料永遠不可變——或者一開始就不去取得它：`finalize_and_delete_metadata_cap` 會從一開始就以不可變的中繼資料來完成該貨幣的設定。無論哪種方式，刪除動作都會記錄在 `Currency` 中，因此該 cap 永遠無法再次被取得。

## 讀取 Currency (Reading a Currency) {#reading-a-currency}

`Currency<T>` 不僅供其建立者使用。作為一個具有衍生地址的共享物件，任何程式碼型別都能找到它，並以不可變參考的方式傳入任何函式，而 registry 為每個欄位都提供了 getter：`decimals`、`name`、`symbol`、`description`、`icon_url`，供給量檢查用的 `is_supply_fixed` 和 `is_supply_burn_only`，以及用來定位此貨幣各項能力（或驗證它們已被刪除，deny cap 屬於_受監管_貨幣，於[下方](#regulated-currencies)介紹）的 `treasury_cap_id`、`metadata_cap_id` 和 `deny_cap_id` 函式。

這使得 coin metadata 成為應用程式能在_鏈上_信賴的東西：借貸協議可以要求作為抵押品的 coin 供給量必須固定，而下方的函式使用 `decimals` 來確保只接受以貨幣整數單位存入的款項：

```move file=packages/samples/sources/programmability/balance-and-coin-4.move anchor=currency_reader

```

## 受監管的貨幣 (Regulated Currencies) {#regulated-currencies}

一種貨幣可以在初始化期間透過對 `CurrencyInitializer` 呼叫 `make_regulated` 來選擇加入監管。這會建立多一項能力——`DenyCapV2<T>`——其擁有者維護一份 _拒絕清單（deny list）_：無法將 `Coin<T>` 作為交易輸入的地址。清單本身存放在保留地址 `0x403` 的 `DenyList` 系統物件中，由
[sui::deny_list](https://docs.sui.io/references/framework/sui/deny_list) 模組管理。此外，受監管的貨幣可以選擇性地支援 _全域暫停（global pause）_，停止該貨幣型別的所有轉帳。此功能是為了像穩定幣這類高度合規要求的資產而存在；大多數貨幣建立時並不需要它。

## 舊版 Coin 中繼資料 (Legacy Coin Metadata) {#legacy-coin-metadata}

在 `CoinRegistry` 出現之前，貨幣是用 `coin::create_currency` 建立的，這會產生一個獨立的
`CoinMetadata<T>` 物件，而非 `Currency<T>`。這個函式已被棄用，但仍有大量用它建立的貨幣
持續在使用中，而且部分應用程式仍預期以 `CoinMetadata` 作為參數。registry 提供了雙向橋接：

- `migrate_legacy_metadata` 會將現有的 `CoinMetadata` 註冊到 registry 中，為其建立
  `Currency<T>`；
- `borrow_legacy_metadata` 會為 registry 原生的 `Currency<T>` 產生一個 `CoinMetadata` 視圖，
  以相容於舊版介面（透過 hot potato 在同一筆交易內回傳）。

新程式碼應一律使用 `coin_registry` 流程。

## 總結 (Summary) {#summary}

- `Coin<T>` 是可替代代幣的主要抽象：一個可以被擁有、轉移，並傳入交易的物件；
- `Balance<T>` 是 `Coin` 內部的計量單位：一個非物件的值，不能被複製或捨棄，只能被移動、拆分和合併——這是型別用來保存資金所嵌入的型別；
- `Currency<T>` 描述代幣型別：中繼資料、供應量狀態，以及法規狀態。它是透過 `CoinRegistry` 系統物件建立的，可以在 `init` 中用 OTW 建立，也可以動態建立——並且可以被任何模組在鏈上*讀取*；
- `Supply<T>` 是計量權威：`Balance` 值被建立和銷毀的唯一關卡。`TreasuryCap<T>` 是它的物件形式——它控制鑄造與銷毀，並且可以被放棄以固定供應量；
- `MetadataCap<T>` 控制中繼資料的更新，可以被刪除以使其變為不可變；
- 代幣的值是以基本單位表示的整數；`Currency` 的 `decimals` 欄位僅用於顯示。

## 延伸閱讀 (Further Reading) {#further-reading}

- Sui 文件中的[貨幣標準](https://docs.sui.io/onchain-finance/fungible-tokens/currency)。
- [sui::coin_registry](https://docs.sui.io/references/framework/sui_sui/coin_registry) 模組文件。
- [sui::coin](https://docs.sui.io/references/framework/sui_sui/coin) 模組文件。
- [sui::balance](https://docs.sui.io/references/framework/sui_sui/balance) 模組文件。
