// Copyright (c) Mysten Labs, Inc.
// SPDX-License-Identifier: Apache-2.0

// ANCHOR: main
module book::coffee_machine {
    /// 咖啡機是共用物件，因此需要 `key` 能力。
    public struct CoffeeMachine has key { id: UID, counter: u16 }

    /// Cup 是被擁有的物件。
    public struct Cup has key, store { id: UID, has_coffee: bool }

    /// 初始化模組並共用 `CoffeeMachine` 物件。
    fun init(ctx: &mut TxContext) {
        transfer::share_object(CoffeeMachine {
            id: object::new(ctx),
            counter: 0
        });
    }

    /// 從空氣中拿出一個杯子。這是快速路徑操作。
    public fun take_cup(ctx: &mut TxContext): Cup {
        Cup { id: object::new(ctx), has_coffee: false }
    }

    /// 製作咖啡並倒入杯子。需要共識。
    public fun make_coffee(machine: &mut CoffeeMachine, cup: &mut Cup) {
        machine.counter = machine.counter + 1;
        cup.has_coffee = true;
    }

    /// 從杯子喝咖啡。這是快速路徑操作。
    public fun drink_coffee(cup: &mut Cup) {
        cup.has_coffee = false;
    }

    /// 放回杯子。這是快速路徑操作。
    public fun put_back(cup: Cup) {
        let Cup { id, has_coffee: _ } = cup;
        id.delete();
    }
}
// ANCHOR_END: main
