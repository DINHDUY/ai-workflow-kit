# Testing Standards

## Requirements

| Requirement | Standard |
|-------------|----------|
| Minimum coverage | ≥90% for domain and application layers |
| Test pattern | Arrange-Act-Assert (AAA) |
| Unit test framework | xUnit |
| Assertions | FluentAssertions |
| Mocking | Moq |
| BDD (optional) | SpecFlow for complex workflows |

## Test Types

| Type | What to Cover | Location |
|------|--------------|----------|
| Unit | Domain logic, application handlers, services | `tests/Unit/` |
| Integration | Repository implementations, API endpoints | `tests/Integration/` |
| Contract | Command/query DTOs, public API shapes | `tests/Contract/` |

---

## Unit Test Structure

```csharp
public class CreateOrderHandlerTests
{
    private readonly Mock<IOrderRepository> _repositoryMock = new();
    private readonly Mock<IUnitOfWork> _unitOfWorkMock = new();
    private readonly CreateOrderHandler _handler;

    public CreateOrderHandlerTests()
    {
        _handler = new CreateOrderHandler(
            _repositoryMock.Object,
            _unitOfWorkMock.Object);
    }

    [Fact]
    public async Task Handle_ValidCommand_CreatesOrderAndReturnsDto()
    {
        // Arrange
        var command = new CreateOrderCommand(CustomerId: "C1", Amount: 100m);
        _repositoryMock
            .Setup(r => r.AddAsync(It.IsAny<Order>(), default))
            .Returns(Task.CompletedTask);

        // Act
        var result = await _handler.Handle(command, CancellationToken.None);

        // Assert
        result.Should().NotBeNull();
        result.CustomerId.Should().Be("C1");
        _repositoryMock.Verify(
            r => r.AddAsync(It.IsAny<Order>(), default),
            Times.Once);
    }

    [Fact]
    public async Task Handle_NullCommand_ThrowsArgumentNullException()
    {
        // Act
        var act = () => _handler.Handle(null!, CancellationToken.None);

        // Assert
        await act.Should().ThrowAsync<ArgumentNullException>();
    }

    [Theory]
    [InlineData(0)]
    [InlineData(-1)]
    public async Task Handle_InvalidAmount_ThrowsDomainException(decimal amount)
    {
        // Arrange
        var command = new CreateOrderCommand(CustomerId: "C1", Amount: amount);

        // Act
        var act = () => _handler.Handle(command, CancellationToken.None);

        // Assert
        await act.Should().ThrowAsync<ArgumentOutOfRangeException>();
    }
}
```

---

## Integration Test Structure

```csharp
// Hits real DB via WebApplicationFactory — no mocks for infrastructure
public class OrdersApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public OrdersApiTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task POST_Orders_ValidRequest_Returns201WithLocation()
    {
        // Arrange
        var request = new CreateOrderRequest(CustomerId: "C1", Amount: 100m);

        // Act
        var response = await _client.PostAsJsonAsync("/api/orders", request);

        // Assert
        response.StatusCode.Should().Be(HttpStatusCode.Created);
        response.Headers.Location.Should().NotBeNull();
        var body = await response.Content.ReadFromJsonAsync<OrderDto>();
        body!.CustomerId.Should().Be("C1");
    }

    [Fact]
    public async Task GET_Orders_NonExistent_Returns404()
    {
        var response = await _client.GetAsync($"/api/orders/{Guid.NewGuid()}");
        response.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }
}
```

---

## Anti-Patterns

- Tests without assertions — the test always passes; means nothing
- Mocking the system under test itself
- Non-descriptive test names: `Test1`, `TestCreateOrder` — use `Method_Scenario_ExpectedResult` or BDD style
- `Thread.Sleep` / `Task.Delay` in tests — use `FakeTimeProvider` or `CancellationToken`
- Testing private methods directly — test through the public interface
- Asserting on `ToString()` — use `.BeEquivalentTo()` for object comparison
- Shared mutable state between tests — each test must be independent
