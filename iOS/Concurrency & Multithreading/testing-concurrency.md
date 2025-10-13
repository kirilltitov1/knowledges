---
type: "thread"
status: "draft"
summary: ""
title: "Testing Concurrency"
---

# Testing Concurrency

### Testing Async Code
```swift
func testAsync() async throws {
    let result = await fetchData()
    XCTAssertEqual(result, expected)
}
```

### Testing with XCTestExpectation
```swift
func testWithExpectation() {
    let expectation = expectation(description: "Async operation")
    
    asyncOperation {
        expectation.fulfill()
    }
    
    wait(for: [expectation], timeout: 5)
}
```

### Testing Actors
```swift
func testActor() async {
    let actor = MyActor()
    let result = await actor.performAction()
    XCTAssertEqual(result, expected)
}
```

### Testing Cancellation
```swift
func testCancellation() async {
    let task = Task { try await longWork() }
    task.cancel()
    do {
        _ = try await task.value
        XCTFail("Expected CancellationError")
    } catch is CancellationError {
        // ok
    } catch {
        XCTFail("Unexpected error: \(error)")
    }
}
```

### Testing Timeout
```swift
func testTimeout() async {
    let slow = Task { try await longWork() }
    let timeout = Task { try await Task.sleep(nanoseconds: 1_000_000_000); return true }
    let didTimeout = await withTaskGroup(of: Bool.self) { g in
        g.addTask { _ = try? await slow.value; return false }
        g.addTask { try? await timeout.value }
        for await v in g { if v { return true } }
        return false
    }
    if didTimeout { slow.cancel() }
    XCTAssertTrue(didTimeout)
}
```

### Tips
- Делайте тесты детерминированными: меньше таймингов, больше синхронизации
- Проверяйте отмену и cleanup
- Используйте TSan и Concurrency Debugger для сложных сценариев


