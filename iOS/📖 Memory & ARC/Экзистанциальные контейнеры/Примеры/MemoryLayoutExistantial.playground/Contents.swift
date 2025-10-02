import UIKit

protocol P { func f() }
protocol Q { func g() }
protocol COnly: AnyObject { func h() }

struct S24: P { var a:Int64=0,b:Int64=0,c:Int64=0; func f(){} } // ~24B
struct S32: P { var t=(Int64(0),Int64(0),Int64(0),Int64(0)); func f(){} } // >24B
final class K: P, Q, COnly { func f(){}; func g(){}; func h(){} }

// Размеры форм
MemoryLayout<Any>.size                   // ~32
MemoryLayout<any P>.size                 // ~40
MemoryLayout<any P & Q>.size             // ~48
MemoryLayout<any P & AnyObject>.size     // ~16
MemoryLayout<any AnyObject>.size         // ~8

// Поведение буфера
let a: Any = 42          // inline
let b: Any = "2012"      // value-репрезентация укладывается в буфер
let c: Any = UIView()    // buffer.word0 = &UIView-instance (объект в heap)
let d: any P = S32()     // большой struct → box в heap, в буфере указатель на box
let e: any P & AnyObject = K() // [object ptr][witness], буфера нет

// Гетерогенный массив
let mixed: [Any] = [42, "2012", UIView()] // каждый элемент — контейнер Any (~32B)
