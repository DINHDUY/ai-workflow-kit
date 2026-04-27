# Clean Architecture — Detailed Reference

## Layer Dependency Rule

```
Presentation (API / Controllers)
    ↓ depends on
Application (Use cases, DTOs, interfaces)
    ↓ depends on
Domain (Entities, value objects, domain logic — zero external dependencies)
    ↑ implemented by
Infrastructure (EF Core, external services, repository implementations)
```

Dependencies flow **inward only**. Domain has zero external dependencies.

---

## Domain Layer

**Contains:**
- Entities (with behavior, not just data)
- Value Objects (`record` types)
- Domain Events (immutable `record` types)
- Domain Services (cross-entity stateless logic)
- Repository **interfaces** (not implementations)
- Domain exceptions

**Must NOT contain:**
- `using Microsoft.EntityFrameworkCore;`
- `[Column]`, `[Table]`, `[Key]` EF attributes
- Any HTTP, database, or external service references
- Infrastructure concerns (logging frameworks, serializers)

**Red flags to call out:**
```csharp
// ❌ EF Core in Domain
using Microsoft.EntityFrameworkCore; // ← Wrong layer
[Column("order_id")]                  // ← Persistence concern in Domain
public class Order { }

// ✅ Pure domain entity
public class Order
{
    public OrderId Id { get; private set; }
    public void AddItem(OrderItem item) { /* business rules */ }
}
```

---

## Application Layer

**Contains:**
- Commands and Queries (CQRS / MediatR)
- Command / Query Handlers
- DTOs (Data Transfer Objects)
- Application service interfaces
- Validation logic (FluentValidation validators)
- Application exceptions

**Must NOT contain:**
- EF Core `DbContext` or raw SQL
- Direct HTTP calls
- Infrastructure implementations

**Good — Application handler:**
```csharp
public class CreateOrderHandler : IRequestHandler<CreateOrderCommand, OrderDto>
{
    private readonly IOrderRepository _repository;
    private readonly IUnitOfWork _unitOfWork;

    public CreateOrderHandler(IOrderRepository repository, IUnitOfWork unitOfWork)
    {
        _repository = repository ?? throw new ArgumentNullException(nameof(repository));
        _unitOfWork = unitOfWork ?? throw new ArgumentNullException(nameof(unitOfWork));
    }

    public async Task<OrderDto> Handle(CreateOrderCommand request, CancellationToken ct)
    {
        var order = Order.Create(request.CustomerId, request.Items);
        await _repository.AddAsync(order, ct);
        await _unitOfWork.SaveChangesAsync(ct);
        return new OrderDto(order.Id, order.TotalAmount);
    }
}
```

---

## Infrastructure Layer

**Contains:**
- EF Core `DbContext` and `IEntityTypeConfiguration<T>` classes
- Repository implementations
- External API clients
- Email / SMS senders
- Cache adapters
- Message broker adapters

**Rules:**
- Implements interfaces defined in Application / Domain layers
- EF entity configuration belongs in `EntityTypeConfiguration<T>`, not as attributes on domain entities

---

## API / Presentation Layer

**Contains:**
- Controllers (thin — delegate immediately to Application via MediatR or service)
- Request / response models
- Middleware and filters
- `Program.cs` / DI registrations

**Must NOT contain:**
- Business logic
- Direct repository calls
- Domain object manipulation

```csharp
// ✅ Good — Thin controller
[HttpPost]
public async Task<IActionResult> CreateOrder(
    [FromBody] CreateOrderRequest request,
    CancellationToken ct)
{
    var command = new CreateOrderCommand(request.CustomerId, request.Items);
    var result = await _mediator.Send(command, ct);
    return Created($"/orders/{result.Id}", result);
}

// ❌ Bad — Business logic and direct DB access in controller
[HttpPost]
public async Task<IActionResult> CreateOrder(CreateOrderRequest request)
{
    var order = new Order { CustomerId = request.CustomerId };
    order.Status = "Pending";                          // ← domain logic in controller
    await _dbContext.Orders.AddAsync(order);           // ← direct DB access
    await _dbContext.SaveChangesAsync();
    return Ok(order);
}
```

---

## Standard Project Structure (.NET 10)

```
src/
├── Domain/              # Entities, value objects, domain services, interfaces
├── Application/         # Use cases, handlers, DTOs, validators
├── Infrastructure/      # EF Core, external services, repositories
└── Presentation/        # Program.cs, controllers, transport config

tests/
├── Unit/               # Domain and application unit tests
├── Integration/        # Repository and API endpoint tests
└── Contract/           # Command/query contract tests
```
