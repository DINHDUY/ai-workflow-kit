# SOLID Principles — Detailed Reference

## Single Responsibility Principle

Each class should have **one reason to change**.

**Red flags:**
- Class name contains "And" or "Manager" handling unrelated concerns
- More than ~5 public methods with unrelated purposes
- A class that talks to the DB, sends email, and formats output

**Bad:**
```csharp
public class OrderService
{
    public void CreateOrder() { }
    public void SendEmail() { }     // ← Email is a separate concern
    public void CalculateTax() { }  // ← Tax is a separate concern
}
```

**Good:**
```csharp
public class OrderCreationService { public void CreateOrder() { } }
public class EmailNotificationService { public void SendEmail() { } }
public class TaxCalculationService { public void CalculateTax() { } }
```

---

## Open/Closed Principle

Open for extension, closed for modification. Add behavior via new implementations, not by editing existing classes.

**Red flags:**
- `switch` or `if/else` chains that must be extended to add new behavior
- Adding a new payment method requires editing `OrderService`

**Good:**
```csharp
public interface IPaymentProcessor
{
    Task ProcessAsync(Payment payment, CancellationToken ct);
}

public class StripePaymentProcessor : IPaymentProcessor { /* ... */ }
public class PayPalPaymentProcessor : IPaymentProcessor { /* ... */ }

// Adding a new processor = new class. OrderService never changes.
```

---

## Liskov Substitution Principle

Subtypes must behave consistently with their base types. Any implementation must be fully substitutable for the abstraction.

**Rules:**
- Implementations MUST NOT throw `NotImplementedException`
- Overrides must not weaken preconditions or strengthen postconditions
- Honor the full contract of every interface method

**Bad:**
```csharp
public class ReadOnlyRepository : IOrderRepository
{
    public Task AddAsync(Order o, CancellationToken ct)
        => throw new NotImplementedException(); // ← Violates LSP
}
```

**Fix:** Define a narrower interface that only declares what the class can honor:
```csharp
public interface IOrderReader
{
    Task<Order?> GetByIdAsync(OrderId id, CancellationToken ct);
}

// ReadOnlyRepository implements IOrderReader only — full contract honored
```

---

## Interface Segregation Principle

No class should be forced to implement methods it doesn't use. Prefer small, focused interfaces.

**Bad:**
```csharp
public interface IOrderService
{
    void Create();
    void Update();
    void Delete();
    void SendEmail();       // ← Unrelated to order CRUD
    void GenerateReport();  // ← Unrelated to order CRUD
}
```

**Good — segregated interfaces:**
```csharp
public interface IOrderCreationService
{
    Task CreateAsync(CreateOrderCommand cmd, CancellationToken ct);
}

public interface IOrderNotificationService
{
    Task NotifyAsync(OrderId id, CancellationToken ct);
}

public interface IOrderReportService
{
    Task<ReportDto> GenerateAsync(DateRange range, CancellationToken ct);
}

// For generic CRUD: IReadable<T, TId>, IWritable<T>, IDeletable<TId>
```

---

## Dependency Inversion Principle

High-level modules must not depend on low-level modules. Both must depend on abstractions.

**Rules:**
- All dependencies injected through constructors
- Depend on interfaces, not concrete classes
- Never use `new ConcreteService()` inside a class

**Bad:**
```csharp
public class OrderProcessor
{
    private readonly SqlOrderRepository _repo = new(); // ← Concrete dep, not injectable
}
```

**Good:**
```csharp
public class OrderProcessor
{
    private readonly IOrderRepository _repo;

    public OrderProcessor(IOrderRepository repo)
    {
        _repo = repo ?? throw new ArgumentNullException(nameof(repo));
    }
}
```
