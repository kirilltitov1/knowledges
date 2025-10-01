---
title: 5. Reactive Programming
type: thread
topics: [Concurrency & Multithreading]
subtopic: 5-reactive-programming
status: draft
---

# 5. Reactive Programming


### Combine Framework

#### Publishers
```swift
let publisher = Just(42)
let arrayPublisher = [1, 2, 3].publisher
let urlPublisher = URLSession.shared.dataTaskPublisher(for: url)
```

#### Subjects
```swift
let subject = PassthroughSubject<String, Never>()
subject.send("Hello")

let currentValueSubject = CurrentValueSubject<Int, Never>(0)
print(currentValueSubject.value)
```

#### Subscribers
```swift
let cancellable = publisher
    .sink { completion in
        // Handle completion
    } receiveValue: { value in
        // Handle value
    }

// Or simple
let cancellable = publisher
    .sink { value in
        print(value)
    }
```

#### @Published
```swift
class ViewModel: ObservableObject {
    @Published var username: String = ""
    @Published var isValid: Bool = false
}
```

#### Operators

**Transforming**
```swift
.map { $0 * 2 }
.flatMap { fetchDetails(for: $0) }
.compactMap { Int($0) }
.scan(0, +) // Accumulate
```

**Filtering**
```swift
.filter { $0 > 10 }
.removeDuplicates()
.debounce(for: .milliseconds(300), scheduler: RunLoop.main)
.throttle(for: .seconds(1), scheduler: RunLoop.main, latest: true)
```

**Combining**
```swift
.merge(with: otherPublisher)
.combineLatest(otherPublisher)
.zip(otherPublisher)
```

**Error Handling**
```swift
.catch { _ in Just(defaultValue) }
.retry(3)
.replaceError(with: defaultValue)
```

**Threading**
```swift
.receive(on: DispatchQueue.main)
.subscribe(on: DispatchQueue.global())
```

#### Custom Publishers
```swift
struct TimerPublisher: Publisher {
    typealias Output = Date
    typealias Failure = Never
    
    func receive<S>(subscriber: S) where S : Subscriber {
        // Implementation
    }
}
```

#### Cancellation
```swift
var cancellables = Set<AnyCancellable>()

publisher
    .sink { value in }
    .store(in: &cancellables)
```

### RxSwift

#### Observables
```swift
let observable = Observable.just(42)
let arrayObservable = Observable.from([1, 2, 3])
```

#### Subjects
```swift
let subject = PublishSubject<String>()
subject.onNext("Hello")

let behaviorSubject = BehaviorSubject(value: 0)
let replaySubject = ReplaySubject<Int>.create(bufferSize: 3)
```

#### Observers
```swift
observable.subscribe(
    onNext: { value in print(value) },
    onError: { error in print(error) },
    onCompleted: { print("Done") }
)
.disposed(by: disposeBag)
```

#### Operators (Similar to Combine)
```swift
.map { $0 * 2 }
.filter { $0 > 10 }
.flatMap { fetchDetails(for: $0) }
.debounce(.milliseconds(300), scheduler: MainScheduler.instance)
.distinctUntilChanged()
```

#### Schedulers
```swift
.observe(on: MainScheduler.instance)
.subscribe(on: ConcurrentDispatchQueueScheduler(qos: .background))
```

#### Disposables
```swift
let disposeBag = DisposeBag()

observable
    .subscribe { event in }
    .disposed(by: disposeBag)
```

