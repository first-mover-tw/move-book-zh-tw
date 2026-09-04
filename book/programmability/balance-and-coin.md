---
description: Sui Move 中的餘額 (Balance)、代幣 (Coin) 與代幣註冊表 (CoinRegistry)：使用貨幣 (Currency) 標準建立同質化代幣、使用國庫權限 (TreasuryCap) 管理供應量，並在鏈上儲存中繼資料。
title: 餘額 (Balance) 與代幣 (Coin)
keywords:
  - Move
  - Sui
  - Move tutorial
  - balance
  - coin
  - tokens
questions:
  - What is Balance and Coin in Move?
  - How do I use Balance and Coin in Move?
  - What is Balance in Move?
  - What is Coin in Move?
answer: 'Balance, Coin, and CoinRegistry in Sui Move: create fungible tokens with the Currency standard, manage supply with TreasuryCap, and store metadata onchain.'
goal:
  description: 'Reader understands balance, Coin, and CoinRegistry in Sui Move: create fungible tokens with the Currency standard, manage supply with TreasuryCap, and store metadata onchain'
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

# 餘額與 Coin (Balance and Coin) {#balance-and-coin}

可互換代幣是最常見的數位資產類型：可彼此交換的價值單位，如同貨幣。在 Sui 上，可互換代幣的主要抽象是 [`Coin`](https://docs.sui.io/references/framework/sui_sui/coin)——錢包持有的物件、交易作為輸入採用的物件，以及應用程式接受作為付款的物件。擁有「10 SUI」表示擁有一個價值為 10 SUI 的 `Coin<SUI>` 物件。

另外兩個輔助型別完善了此標準——一個位於 `Coin` 之下一層，另一個位於其上一層：

- [`Balance`](https://docs.sui.io/references/framework/sui_sui/balance)——`Coin` 內的原始數量：沒有物件 ID 的純值，應用程式會用它來儲存及累積資金；
- [`Currency`](https://docs.sui.io/references/framework/sui_sui/coin_registry)——描述代幣型別本身的共享物件：其中繼資料、供應量及監管狀態。

本節將逐一說明這三者，並示範如何透過 `sui::coin_registry` 模組建立貨幣——這是執行此操作的標準方式。

## 餘額 (Balance) {#balance}

`Balance<T>` 型別定義於 `sui::balance` 模組中。它是具備 `store`
能力的純值，而非物件：它沒有 `UID`，也沒有自身的儲存額外負擔。這使它成為*保管*資金時的首選型別：每當應用程式需要在
自身型別內儲存或累積價值時——例如金庫、流動性池或託管——就應內嵌 `Balance`，而非 `Coin`。

```move
/// 可儲存的餘額——Coin 型別的內部結構。
/// 可用於儲存不需要 key 能力的代幣。
public struct Balance<phantom T> has store {
    value: u64,
}
```

[虛擬型別參數](./../move-basics/generics#phantom-type-parameters) `T` 會讓不同餘額彼此區分：`Balance<GOLD>` 與 `Balance<DBL>` 是不同且不可互換的型別，儘管兩者都只儲存一個 `u64`。

`Balance` 沒有 `copy`、沒有 `drop`，也沒有可建立非零值的公開建構子。餘額只能透過增加 `T` 的總供給量來建立，也只能透過減少總供給量而消失。其間的一切——分割、合併、儲存——都只是移動價值。這是套用於金錢的[所有權](./../move-basics/ownership-and-scope)保證：沒有重複，也不會意外遺失。

```move file=packages/samples/sources/programmability/balance-and-coin.move anchor=balance

```

## 代幣 (Coin) {#coin}

`Balance` 無法在儲存空間中獨立存在——它必須包裝在物件中。`sui::coin::Coin` 型別是標準包裝器：

```move
/// 價值為 `value` 的 `T` 型別代幣。
public struct Coin<phantom T> has key, store {
    id: UID,
    balance: Balance<T>,
}
```

具備 `key` 與 `store` 的 `Coin` 是完整的物件：它可以由帳戶擁有、轉移，並作為輸入傳入交易。用於支付交易 gas 的 gas 物件是 `Coin<SUI>`。這也形成了標準的經驗法則：邊界使用 `Coin`，內部使用 `Balance`。資金以 `Coin` 形式進入應用程式，以 `Balance` 形式儲存及累積，並再次以 `Coin` 形式離開。

API 與 `Balance` 對應——在兩者之間分割、合併及轉換：

```move file=packages/samples/sources/programmability/balance-and-coin.move anchor=coin

```

> 上述範例透過僅供測試使用的 `coin::mint_for_testing` 與 `balance::create_for_testing` 函式憑空建立其 `Coin` 和 `Balance`——這些是測試代幣處理原始碼的標準工具，請參閱[在測試中使用系統物件](./../testing/using-system-objects)。

在交易中，代幣會受到特殊處理：原生的 `SplitCoins` 與 `MergeCoins` [命令](./../concepts/what-is-a-transaction#commands)可直接操作代幣，因此錢包無須呼叫任何模組函式，即可準備精確付款——甚至可從 gas 代幣中分割出來。這就是模組很少需要自行公開分割或合併功能的原因。

`sui::coin` 模組也提供 `coin::take` 和 `coin::put` 輔助函式，將轉換與分割／合併步驟結合：`take` 會從 `Balance` 分割出一個 `Coin`，而 `put` 會將一個 `Coin` 合併至 `Balance`。當應用程式將資金儲存為 `Balance` 並以 `Coin` 形式轉出時，這些函式相當實用。

> 代幣物件不是持有可互換價值的唯一方式：較新的機制會將其直接保留在地址中，以不需管理物件的持續累計總額表示。它建立於此處說明的型別之上，詳見[地址餘額](./address-balances)章節。

## 貨幣與 Coin Registry (Currency and the Coin Registry) {#currency-and-the-coin-registry}

單一 `Coin<T>` 並未說明代幣 `T` 本身的任何資訊：它的名稱、符號、使用的小數位數，或供應量的管理方式。這些資訊會針對每種型別儲存在一個 `Currency<T>` 物件中，而所有貨幣皆由 `CoinRegistry` 追蹤——這是一個保留地址為 `0xc` 的系統物件：

```move
/// 位於地址 `0xc` 的系統物件，儲存所有
/// 已註冊代幣型別的代幣資料。
public struct CoinRegistry has key { id: UID }
```

`Currency<T>` 物件包含關於代幣型別 `T` 的所有資訊：

```move
/// Currency 儲存名稱、符號、小數位數、icon_url 與
/// 描述等中繼資料，以及供應量狀態（選用）和監管狀態。
public struct Currency<phantom T> has key {
    id: UID,
    /// 代幣用於顯示的小數位數。
    decimals: u8,
    /// 供人閱讀的代幣名稱。
    name: String,
    /// 代幣的簡短符號／代號。
    symbol: String,
    /// 代幣的詳細描述。
    description: String,
    /// 代幣圖示／標誌的 URL。
    icon_url: String,
    /// 代幣目前的供應量狀態（固定、僅銷毀或未知）。
    supply: Option<SupplyState<T>>,
    /// 代幣的監管狀態（受監管且具有拒絕能力，或未知）。
    regulated: RegulatedState,
    /// 此代幣型別的 treasury cap ID（若已註冊）。
    treasury_cap_id: Option<ID>,
    /// 此代幣型別的中繼資料能力 ID（若已取得）。
    metadata_cap_id: MetadataCapState,
    /// 用於擴充的額外欄位。
    extra_fields: VecMap<String, ExtraField>,
}
```

這些欄位大多會在本頁各自的章節中介紹：供應量狀態、監管狀態，以及兩項能力都會在下方說明。然而，有一個欄位值得立刻注意：`decimals`。Move 沒有分數——`Coin` 的值是單純的整數，用來計算貨幣的最小單位，而 `decimals` 則告知用戶端應在何處放置小數點，僅供*顯示*使用。當 `decimals = 8` 時，值為 `100_000_000` 的 `Coin` 會顯示為 `1` 枚代幣；原生 SUI 貨幣有 9 位小數，其基本單位甚至有專屬名稱——MIST。Move 原始碼中的金額——鑄造、分割、比較——一律以基本單位表示。

`coin_registry` 模組是建立貨幣的*唯一*方式：它取代了原本的 `coin::create_currency` 函式，後者將中繼資料儲存在獨立的 `CoinMetadata` 物件中（我們會在[本節結尾](#legacy-coin-metadata)說明差異）。它提供兩種建立貨幣的方式，兩者都會產生相同結果：一個具有[衍生地址](https://docs.sui.io/references/framework/sui_sui/derived_object)的共享 `Currency<T>` 物件，因此無須知道物件 ID，即可找到任何代幣型別的中繼資料。

### 在 `init` 中建立貨幣 (Creating a Currency in `init`) {#creating-a-currency-in-init}

最常見的流程會使用 [One-Time Witness](./one-time-witness)，以保證只能在[模組初始化函式](./module-initializer)中為該型別建立一次貨幣：

```move file=packages/samples/sources/programmability/balance-and-coin-2.move anchor=gold

```

`new_currency_with_otw` 呼叫會回傳兩個值：

- `CurrencyInitializer`——用於在發佈前設定貨幣的暫時值。它無法儲存或丟棄，因此在透過 `finalize` 呼叫消耗它之前，交易無法成功（這項技術會在 [Hot Potato Pattern](./hot-potato-pattern) 章節中探討）；
- `TreasuryCap<T>`——控制鑄造與銷毀的[能力](./capability)，會在下方的[供應量與 TreasuryCap](#supply-and-treasurycap)章節中探討。

`finalize` 呼叫還會回傳另一項能力——控制貨幣中繼資料更新的 `MetadataCap<T>`。不過，在 OTW 流程中，`finalize` 並不會完成註冊。由於 `init` 在發佈期間執行，此時尚無法將 `CoinRegistry` 作為引數傳入，因此 `Currency<GOLD>` 物件會繞行一段路：`finalize` 會將它轉移至 registry 的地址，在那裡等待第二個收尾步驟——`finalize_registration`：

```move
/// 代幣中繼資料「otw」初始化的第二個步驟，接收
/// 從 init 轉移而來的 `Currency<T>`，並將其轉換為
/// 具有「衍生地址」的共享物件。
///
/// 任何人都可以執行。
public fun finalize_registration<T>(
    registry: &mut CoinRegistry,
    currency: Receiving<Currency<T>>,
    _ctx: &mut TxContext,
);
```

此函式會[接收](./../storage/transfer-to-object)傳送至 registry 的 `Currency<T>`，並將其重新建立為具有衍生地址的共享物件。在呼叫它之前，註冊尚未完成：`Currency<GOLD>` 並非共享物件、無法透過其衍生地址找到，也無法傳入任何讀取或更新它的函式。此呼叫不需要權限——任何人都可以執行，且索引器通常會這麼做——但不應聽天由命：

> 請將 `finalize_registration` 視為 OTW 流程的必要部分，而非可選的清理工作。發佈者應在發佈後立即於後續交易中呼叫它——唯有如此，貨幣才算完整註冊並可使用。

### 動態建立貨幣 (Creating a Currency Dynamically) {#creating-a-currency-dynamically}

第二種流程不需要 OTW，且可在套件發佈後的任何時間執行——例如在按需建立貨幣的應用程式中。`new_currency` 函式會直接取得 `CoinRegistry`，而 `Currency<T>` 會在 `finalize` 時立即成為共享物件，無須額外的註冊步驟：

```move file=packages/samples/sources/programmability/balance-and-coin-3.move anchor=doubloon

```

### 一種型別，兩種形式 (One Type, Two Shapes) {#one-type-two-shapes}

兩種流程皆使用標記型別 `T` 為貨幣定義面額，但它們對 `T` 要求不同的形式，分別對應各自證明貨幣只會建立一次的方式：

- `new_currency_with_otw` 接受具有 `drop` 的 `T`——具體而言，是 [One-Time Witness](./one-time-witness)：一個僅具 `drop`、沒有欄位，且以其模組命名的結構。證明就是見證*值*本身：它只存在一次、會被呼叫消耗，而且永遠無法再次產生——因此該貨幣也無法再次建立。
- `new_currency` 接受僅具 _key_ 的 `T`——僅有 `has key`，不具其他能力，且只有唯一的 `id: UID` 欄位。不會傳入 `T` 的執行個體，只會傳入型別引數，因此沒有見證值可證明任何事情。取而代之的是兩項檢查：`new_currency` 受到[內部約束](./../storage/internal-constraint)限制——如同 `sui::event::emit`，它只能以呼叫模組中定義的型別呼叫——而若 `Currency<T>` 已完成註冊，registry 便會中止。

僅具 key 的型別不能有 `drop`，因此相同型別永遠無法同時用於兩種流程。

## 供應量與 TreasuryCap (Supply and TreasuryCap) {#supply-and-treasurycap}

[Balance](#balance) 章節說明了，價值只能藉由增加 `T` 的總供應量來建立，也只能藉由減少總供應量來消失。同時執行這兩項操作的型別是 `Supply<T>`，其在 `sui::balance` 中定義為 `Balance` 的帳務對應物：

```move
module sui::balance;

/// T 的供應量。用於鑄造與銷毀。
public struct Supply<phantom T> has store {
    value: u64,
}

/// 將供應量增加 `value`，建立新的 `Balance<T>`。
public fun increase_supply<T>(self: &mut Supply<T>, value: u64): Balance<T>;

/// 銷毀一個 `Balance<T>`，依其價值減少供應量。
public fun decrease_supply<T>(self: &mut Supply<T>, balance: Balance<T>): u64;
```

這兩個函式是價值進入與離開流通的唯一關卡，因此現存的每個 `Balance<T>` 單位都會由 `Supply<T>` 記錄：供應量中的數字永遠等於所有 `T` 餘額的總和。

正如 `Coin` 是 `Balance` 的物件形式，`TreasuryCap<T>`——兩種建立流程都會回傳的能力——則是 `Supply` 的物件形式：

```move
module sui::coin;

/// 允許持有者鑄造與銷毀
/// `T` 型別代幣的能力。可轉移
public struct TreasuryCap<phantom T> has key, store {
    id: UID,
    total_supply: Supply<T>,
}
```

持有 `TreasuryCap` _就是_ 持有供應量權限。其 `mint` 與 `burn` 函式是供應量操作的薄包裝：`mint` 增加供應量並將新的 `Balance` 包裝為 `Coin`，`burn` 則解開 `Coin` 包裝，並依其價值減少供應量。只要 `TreasuryCap` 存在，就能透過 `total_supply` 讀取目前總量。

```move file=packages/samples/sources/programmability/balance-and-coin-3.move anchor=mint_burn

```

持有 `TreasuryCap` 的人控制供應量，因此此能力最終歸屬何處是一項設計決策：由發布者持有以管理供應量、儲存在應用程式物件中以進行程式化鑄造，或完全放棄——如下文所述。

> `Supply` 也可以獨立存在：`balance::create_supply` 會將見證轉換為原始的 `Supply<T>`——事實上，這正是我們用來介紹 [Witness pattern](./witness-pattern) 的範例——而 `treasury_into_supply` 會從 `TreasuryCap` 擷取供應量。這些都是低階工具：透過 registry 建立的貨幣應保留完整的 `TreasuryCap`，因為下文說明的供應量狀態會對該能力進行操作。

## 供應狀態 (Supply States) {#supply-states}

預設情況下，貨幣的供應量是彈性的——`Currency<T>` 物件會將其記錄為 `Unknown`，
而 `TreasuryCap` 可以自由鑄造與銷毀。登錄表支援兩種不可逆轉的轉換，
兩者都會消耗 `TreasuryCap`：

- `make_supply_fixed` - 供應量之後永遠無法再變更。上述的 `Doubloon` 範例使用此方式：
  它會預先鑄造全部供應量，並在同一次呼叫中將其固定；
- `make_supply_burn_only` - 不再允許鑄造，但任何人都可以透過
  `coin_registry::burn` 與 `burn_balance` 函式銷毀代幣；這些函式會取得共享的 `Currency` 物件，
  並永久減少供應量。

兩種方式都可以在初始化期間（於 `CurrencyInitializer` 上）套用，或稍後於共享的
`Currency<T>` 物件上套用。消耗此能力不只是形式：此轉換會解構 `TreasuryCap`，並將其 `Supply<T>`
_移入_ `Currency` 物件——因此從該時點起，`Currency` 本身會追蹤總供應量，
並可透過 `total_supply` 在鏈上讀取。

## 管理中繼資料 (Managing Metadata) {#managing-metadata}

貨幣的名稱、符號、描述與圖示 URL 可在建立後透過 `set_name`、`set_symbol`、`set_description` 與 `set_icon_url` 函式更新；每個函式都需要 `MetadataCap<T>` 的參考。與 `TreasuryCap` 一樣，`MetadataCap` 可透過 `delete_metadata_cap` 刪除，使中繼資料永久不可變；或者一開始就不曾領取：`finalize_and_delete_metadata_cap` 會從一開始便以不可變的中繼資料完成貨幣定案。無論採用哪種方式，刪除都會記錄在 `Currency` 中，因此永遠無法再次領取該 cap。

## 讀取貨幣 (Reading a Currency) {#reading-a-currency}

`Currency<T>` 不僅供其建立者使用。作為具有衍生地址的共享物件，它可針對任何代幣類型被找到，並透過不可變參考傳遞至任何函式；登錄表也為每個欄位提供 getter：`decimals`、`name`、`symbol`、`description`、`icon_url`、供應量檢查 `is_supply_fixed` 與 `is_supply_burn_only`，以及用於定位該貨幣能力的 `treasury_cap_id`、`metadata_cap_id` 與 `deny_cap_id` 函式——或驗證它們是否已被刪除（deny cap 屬於*受監管的*貨幣，將於[下方](#regulated-currencies)說明）。

這讓代幣中繼資料成為應用程式可在*鏈上*依賴的資訊：借貸協定可以要求抵押代幣的供應量固定，而下方函式使用 `decimals`，僅接受以貨幣完整單位計算的存款：

```move file=packages/samples/sources/programmability/balance-and-coin-4.move anchor=currency_reader

```

## 受監管貨幣 (Regulated Currencies) {#regulated-currencies}

貨幣可在初始化期間於 `CurrencyInitializer` 上呼叫 `make_regulated`，選擇啟用監管功能。這會建立另一項權能——`DenyCapV2<T>`——其擁有者會維護一份*拒絕清單*：其中的地址無法將 `Coin<T>` 用作交易輸入。清單本身位於保留地址 `0x403` 的 `DenyList` 系統物件中，並由 [sui::deny_list](https://docs.sui.io/references/framework/sui/deny_list) 模組管理。受監管貨幣也可選擇支援*全域暫停*，以停止該貨幣類型的所有轉移。此功能適用於穩定幣等高度重視合規性的資產；大多數貨幣建立時不會啟用此功能。

## 舊版 Coin 中繼資料 (Legacy Coin Metadata) {#legacy-coin-metadata}

在 `CoinRegistry` 之前，貨幣是透過 `coin::create_currency` 建立，該函式會產生獨立的
`CoinMetadata<T>` 物件，而非 `Currency<T>`。此函式已淘汰，但許多使用它建立的貨幣仍在運作，
而且有些應用程式仍預期將 `CoinMetadata` 作為引數。Registry 提供雙向橋接：

- `migrate_legacy_metadata` 會在 Registry 中註冊既有的 `CoinMetadata`，並為其建立
  `Currency<T>`；
- `borrow_legacy_metadata` 會產生 Registry 原生 `Currency<T>` 的 `CoinMetadata` 檢視，以便
  相容於較舊的介面（透過 hot potato 在同一筆交易中回傳）。

新的原始碼應一律使用 `coin_registry` 流程。

## 摘要 (Summary) {#summary}

- `Coin<T>` 是可替代代幣的主要抽象：可被擁有、轉移，並傳入交易的物件；
- `Balance<T>` 是 `Coin` 內部的記帳單位：不可複製或丟棄的非物件值，只能移動、拆分與合併；型別應用程式會內嵌它來保留資金；
- `Currency<T>` 描述代幣型別：中繼資料、供應量狀態及監管狀態。它會透過 `CoinRegistry` 系統物件建立，可在 `init` 中使用 OTW 建立，或動態建立；任何模組都能在鏈上*讀取*它；
- `Supply<T>` 是記帳權限：建立與銷毀 `Balance` 值的唯一關卡。`TreasuryCap<T>` 是它的物件形式，控制鑄造與銷毀，且可放棄以固定供應量；
- `MetadataCap<T>` 控制中繼資料更新，且可刪除以使其不可變；
- 代幣值是基本單位的整數；`Currency` 的 `decimals` 欄位僅用於顯示。

## 延伸閱讀 (Further Reading) {#further-reading}

- Sui 文件中的[貨幣標準](https://docs.sui.io/onchain-finance/fungible-tokens/currency)。
- [sui::coin_registry](https://docs.sui.io/references/framework/sui_sui/coin_registry) 模組文件。
- [sui::coin](https://docs.sui.io/references/framework/sui_sui/coin) 模組文件。
- [sui::balance](https://docs.sui.io/references/framework/sui_sui/balance) 模組文件。
