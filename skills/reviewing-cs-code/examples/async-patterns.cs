// Async/Await Patterns — Code Examples
// Rule: all I/O async, never .Result/.Wait(), always CancellationToken, always Async suffix

namespace Examples.AsyncPatterns;

// ── Bad Patterns ─────────────────────────────────────

class OrderController_SyncBlock
{
    private readonly IOrderRepository _repository;

    // ❌ Bad: Blocking async call — deadlock risk in ASP.NET Core
    public OrderDto GetOrder(Guid id)
    {
        return _repository.GetOrderAsync(new OrderId(id), CancellationToken.None).Result;
        //                                                                         ^^^^^^ Deadlock risk
    }
}

class OrderService_MissingToken
{
    private readonly IOrderRepository _repository;

    // ❌ Bad: Missing CancellationToken — request cancellations are ignored
    public async Task<OrderDto?> GetOrderAsync(OrderId id)
    {
        var order = await _repository.GetByIdAsync(id, CancellationToken.None);
        return order is null ? null : new OrderDto(order.Id, order.TotalAmount);
    }
}

class OrderService_MissingSuffix
{
    private readonly IOrderRepository _repository;

    // ❌ Bad: Async method name missing "Async" suffix
    public async Task<OrderDto?> GetOrder(OrderId id, CancellationToken ct)
    {
        var order = await _repository.GetByIdAsync(id, ct);
        return order is null ? null : new OrderDto(order.Id, order.TotalAmount);
    }
}

// ── Good Patterns ─────────────────────────────────────

class OrderService_Good
{
    private readonly IOrderRepository _repository;

    public OrderService_Good(IOrderRepository repository)
        => _repository = repository ?? throw new ArgumentNullException(nameof(repository));

    // ✅ Good: Proper async signature with CancellationToken propagation
    public async Task<OrderDto> GetOrderAsync(OrderId id, CancellationToken ct)
    {
        var order = await _repository.GetByIdAsync(id, ct); // ct propagated
        return order is null
            ? throw new OrderNotFoundException(id)
            : new OrderDto(order.Id, order.TotalAmount);
    }
}

class OrderRepository_Library
{
    private readonly AppDbContext _context;

    // ✅ Good: ConfigureAwait(false) in library/infrastructure code
    // NOT used in ASP.NET Core request handlers — only in reusable library code
    public async Task<Order?> GetByIdAsync(OrderId id, CancellationToken ct)
    {
        return await _context.Orders
            .FirstOrDefaultAsync(o => o.Id == id, ct)
            .ConfigureAwait(false); // ← library code only
    }

    // ✅ Good: Streaming large result sets with IAsyncEnumerable
    public async IAsyncEnumerable<Order> StreamPendingOrdersAsync(
        [EnumeratorCancellation] CancellationToken ct)
    {
        await foreach (var order in _context.Orders
            .Where(o => o.Status == OrderStatus.Pending)
            .AsAsyncEnumerable()
            .WithCancellation(ct))
        {
            yield return order;
        }
    }
}
