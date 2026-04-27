// Error Handling Patterns — Code Examples
// See references/error-handling.md for API mapping and full anti-pattern checklist

namespace Examples.ErrorHandling;

// ── Custom Exception Hierarchy ────────────────────────

public abstract class DomainException : Exception
{
    protected DomainException(string message) : base(message) { }
}

public class OrderNotFoundException : DomainException
{
    public OrderNotFoundException(OrderId id)
        : base($"Order {id.Value} was not found.") { }
}

public class InvalidOrderStateException : DomainException
{
    public InvalidOrderStateException(OrderId id, OrderStatus current, OrderStatus required)
        : base($"Order {id.Value} must be in '{required}' state, but is '{current}'.") { }
}

// ── Bad Patterns ─────────────────────────────────────

class OrderService_BadHandling
{
    public async Task ProcessAsync(OrderId id, CancellationToken ct)
    {
        try { /* ... */ }
        catch (Exception) { }                           // ❌ Silent swallow

        try { /* ... */ }
        catch (Exception ex) { throw new Exception(ex.StackTrace); } // ❌ Stack trace to caller

        try { /* ... */ }
        catch (Exception ex) { _logger.LogError("Error"); }  // ❌ No context in log
    }
}

// ── Good Patterns ─────────────────────────────────────

class OrderService_GoodHandling
{
    private readonly ILogger<OrderService_GoodHandling> _logger;
    private readonly IOrderRepository _repository;

    public OrderService_GoodHandling(
        ILogger<OrderService_GoodHandling> logger,
        IOrderRepository repository)
    {
        _logger = logger;
        _repository = repository;
    }

    public async Task ProcessOrderAsync(OrderId id, CancellationToken ct)
    {
        try
        {
            var order = await _repository.GetByIdAsync(id, ct)
                ?? throw new OrderNotFoundException(id);

            order.Place();
            await _repository.UpdateAsync(order, ct);
        }
        catch (OrderNotFoundException ex)
        {
            // ✅ Domain exception: Warning severity, re-throw for API layer to map to 404
            _logger.LogWarning(ex,
                "Order {OrderId} not found during {Operation}",
                id, nameof(ProcessOrderAsync));
            throw;
        }
        catch (DomainException ex)
        {
            // ✅ Domain rule violation: Warning severity
            _logger.LogWarning(ex,
                "Domain rule violated for order {OrderId} in {Operation}",
                id, nameof(ProcessOrderAsync));
            throw;
        }
        catch (OperationCanceledException)
        {
            // ✅ Cancellation: re-throw without logging (not an error)
            throw;
        }
        catch (Exception ex)
        {
            // ✅ Unexpected: Error severity, clean message returned to caller
            _logger.LogError(ex,
                "Unexpected error in {Operation} for order {OrderId}",
                nameof(ProcessOrderAsync), id);
            throw new ApplicationException("An error occurred processing your request.");
        }
    }
}
