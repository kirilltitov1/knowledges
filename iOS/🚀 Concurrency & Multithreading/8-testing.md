---
title: 8. Testing
type: thread
topics: [Concurrency & Multithreading]
subtopic: 8-testing
status: draft
---

# 8. Testing


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

