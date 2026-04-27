// SOLID Principles — Code Examples
// See references/solid-principles.md for explanations

namespace Examples.Solid;

// ── Single Responsibility Principle ───────────────────

// ❌ Bad: Multiple responsibilities in one class
class OrderService_Bad
{
    public void CreateOrder() { }
    public void SendEmail() { }      // Unrelated concern
    public void CalculateTax() { }   // Unrelated concern
}

// ✅ Good: Each class has one reason to change
class OrderCreationService { public void CreateOrder() { } }
class EmailNotificationService { public void SendEmail() { } }
class TaxCalculationService { public void CalculateTax() { } }

// ── Open/Closed Principle ──────────────────────────────

// ✅ Good: New payment methods added without modifying existing code
interface IPaymentProcessor
{
    Task ProcessAsync(Payment payment, CancellationToken ct);
}
class StripePaymentProcessor : IPaymentProcessor
{
    public Task ProcessAsync(Payment payment, CancellationToken ct) => Task.CompletedTask;
}
class PayPalPaymentProcessor : IPaymentProcessor
{
    public Task ProcessAsync(Payment payment, CancellationToken ct) => Task.CompletedTask;
}

// ── Liskov Substitution Principle ─────────────────────

// ❌ Bad: NotImplementedException violates the interface contract
class ReadOnlyRepository_Bad : IOrderRepository
{
    public Task<Order?> GetByIdAsync(OrderId id, CancellationToken ct)
        => Task.FromResult<Order?>(null);

    public Task AddAsync(Order o, CancellationToken ct)
        => throw new NotImplementedException(); // ← LSP violation — callers can't trust this
}

// ✅ Good: Narrower interface that the class can fully honor
interface IOrderReader
{
    Task<Order?> GetByIdAsync(OrderId id, CancellationToken ct);
}

class ReadOnlyRepository_Good : IOrderReader
{
    public Task<Order?> GetByIdAsync(OrderId id, CancellationToken ct)
        => Task.FromResult<Order?>(null); // Fully implemented — contract honored
}

// ── Interface Segregation Principle ───────────────────

// ❌ Bad: Fat interface forces unrelated implementations
interface IOrderService_Fat
{
    void Create();
    void Update();
    void Delete();
    void SendEmail();       // Unrelated to CRUD
    void GenerateReport();  // Unrelated to CRUD
}

// ✅ Good: Small, focused interfaces
interface IOrderCreationService
{
    Task CreateAsync(CreateOrderCommand cmd, CancellationToken ct);
}
interface IOrderNotificationService
{
    Task NotifyAsync(OrderId id, CancellationToken ct);
}

// ── Dependency Inversion Principle ────────────────────

// ❌ Bad: Concrete dependency, not injectable
class OrderProcessor_Bad
{
    private readonly SqlOrderRepository _repo = new(); // ← Not injectable, not testable
}

// ✅ Good: Depends on abstraction, injected via constructor
class OrderProcessor_Good
{
    private readonly IOrderRepository _repo;

    public OrderProcessor_Good(IOrderRepository repo)
    {
        _repo = repo ?? throw new ArgumentNullException(nameof(repo));
    }
}
