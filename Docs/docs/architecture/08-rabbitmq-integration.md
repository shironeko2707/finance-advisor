# RabbitMQ Integration Architecture

## Overview

This document describes the RabbitMQ message queue architecture for the Khengleong system with the integrated Qlib Advisor & Predictor service.

## Queue Topology

### Current Queues (Existing)

1. **report_requests** (Existing)
   - Purpose: Request queue for report generation
   - Publisher: API.FastPy
   - Consumer: AI Service
   - Message Type: `ReportRequest`
   - Durability: Durable
   - Auto-Delete: No
   - TTL: None (persistent)

2. **report_responses** (Existing)
   - Purpose: Response queue for completed reports
   - Publisher: AI Service (currently) → Will be Report Module (future)
   - Consumer: API.FastPy
   - Message Type: `ReportResponse`
   - Durability: Durable
   - Auto-Delete: No
   - TTL: 24 hours

### New Queues (Qlib Integration)

3. **ai_extraction_complete** (NEW)
   - Purpose: Notification when AI extraction finishes
   - Publisher: AI Service
   - Consumer: Qlib Service
   - Message Type: `AIExtractionCompleteMessage`
   - Durability: Durable
   - Auto-Delete: No
   - TTL: 1 hour
   - Dead Letter Exchange: `dlx_qlib`

4. **qlib_predictions_ready** (NEW)
   - Purpose: Notification when Qlib predictions are ready
   - Publisher: Qlib Service
   - Consumer: Report Module (within API.FastPy)
   - Message Type: `QlibPredictionsReadyMessage`
   - Durability: Durable
   - Auto-Delete: No
   - TTL: 1 hour
   - Dead Letter Exchange: `dlx_reports`

5. **qlib_predictions_dlq** (NEW - Dead Letter Queue)
   - Purpose: Failed/expired messages from ai_extraction_complete
   - Publisher: RabbitMQ (automatic)
   - Consumer: Admin/Monitoring Service
   - Durability: Durable
   - Auto-Delete: No
   - TTL: 7 days

---

## Message Flow Diagram

```
┌──────────┐                                                              ┌──────────┐
│  User    │                                                              │  User    │
└────┬─────┘                                                              └────▲─────┘
     │ 1. Upload Files                                                         │ 11. Download
     ▼                                                                          │
┌─────────────────┐                                                   ┌─────────┴───────┐
│  API.FastPy     │                                                   │  API.FastPy     │
│  (Backend)      │                                                   │  (Backend)      │
└────┬────────────┘                                                   └─────────▲───────┘
     │ 2. Publish                                                               │ 10. Consume
     ▼                                                                           │
┌─────────────────────┐                                                         │
│   RabbitMQ Queue    │                                             ┌───────────┴───────────┐
│  report_requests    │                                             │   RabbitMQ Queue      │
└────┬────────────────┘                                             │  report_responses     │
     │ 3. Consume                                                   └───────────▲───────────┘
     ▼                                                                           │ 9. Publish
┌─────────────────┐                                                             │
│   AI Service    │                                                ┌────────────┴──────────┐
│  (Extraction)   │                                                │  Report Module        │
└────┬────────────┘                                                │  (Excel Generation)   │
     │ 4. Extract Data                                             └────────────▲──────────┘
     │ 5. Publish                                                               │ 8. Consume
     ▼                                                                           │
┌──────────────────────┐                                          ┌──────────────┴──────────┐
│   RabbitMQ Queue     │                                          │   RabbitMQ Queue        │
│ ai_extraction_       │                                          │ qlib_predictions_ready  │
│    complete          │                                          └──────────────▲──────────┘
└────┬─────────────────┘                                                         │ 7. Publish
     │ 6. Consume                                                                │
     ▼                                                                            │
┌─────────────────┐                                                  ┌───────────┴─────────┐
│  Qlib Service   │─────────────────────────────────────────────────▶│   Qlib Service      │
│  (Consumer)     │  Forecast, Analyze, Recommend                    │   (Publisher)       │
└─────────────────┘                                                  └─────────────────────┘
```

---

## Detailed Queue Configuration

### 1. report_requests Queue

```python
# Existing queue configuration (no changes)
queue_config = {
    "name": "report_requests",
    "durable": True,
    "auto_delete": False,
    "arguments": {
        "x-message-ttl": None,  # No expiry
        "x-max-length": 1000,   # Max 1000 messages
        "x-overflow": "reject-publish"  # Reject new messages when full
    }
}
```

**Routing Key**: `report.request`
**Exchange**: `` (default exchange)

---

### 2. ai_extraction_complete Queue

```python
queue_config = {
    "name": "ai_extraction_complete",
    "durable": True,
    "auto_delete": False,
    "arguments": {
        "x-message-ttl": 3600000,  # 1 hour TTL
        "x-max-length": 500,
        "x-overflow": "drop-head",  # Drop oldest messages
        "x-dead-letter-exchange": "dlx_qlib",
        "x-dead-letter-routing-key": "qlib.extraction.failed"
    }
}
```

**Routing Key**: `ai.extraction.complete`
**Exchange**: `khengleong.direct` (new direct exchange)
**Consumer Prefetch**: 1 (process one message at a time)

**Publisher (AI Service) - Publish Code**:

```python
import json
from aio_pika import connect_robust, Message, DeliveryMode

async def publish_extraction_complete(request_id, report_id, extracted_data):
    connection = await connect_robust(rabbitmq_url)
    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        "khengleong.direct",
        type="direct",
        durable=True
    )

    message_body = {
        "request_id": request_id,
        "report_id": report_id,
        "timestamp": datetime.now().isoformat(),
        "extraction_status": "success",
        "extracted_data": extracted_data,
        "document_metadata": {...}
    }

    message = Message(
        body=json.dumps(message_body).encode(),
        delivery_mode=DeliveryMode.PERSISTENT,
        content_type="application/json",
        content_encoding="utf-8",
        headers={
            "x-request-id": request_id,
            "x-source": "ai_service"
        }
    )

    await exchange.publish(
        message,
        routing_key="ai.extraction.complete"
    )

    logger.info(f"Published AI extraction complete for {request_id}")
    await connection.close()
```

**Consumer (Qlib Service) - Consume Code**:

```python
async def start_extraction_consumer():
    connection = await connect_robust(rabbitmq_url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=1)  # Process one at a time

    queue = await channel.declare_queue(
        "ai_extraction_complete",
        durable=True,
        arguments={
            "x-message-ttl": 3600000,
            "x-dead-letter-exchange": "dlx_qlib"
        }
    )

    async def process_message(message):
        async with message.process(requeue=True):  # Requeue on failure
            try:
                data = json.loads(message.body.decode())
                request_id = data["request_id"]

                logger.info(f"Processing extraction for {request_id}")

                # Process with Qlib
                predictions = await qlib_service.generate_predictions(data)

                # Publish predictions
                await publish_predictions(request_id, predictions)

            except Exception as e:
                logger.error(f"Failed to process: {e}")
                raise  # Requeue message

    await queue.consume(process_message)
    logger.info("Started consuming ai_extraction_complete queue")

    await asyncio.Future()  # Run forever
```

---

### 3. qlib_predictions_ready Queue

```python
queue_config = {
    "name": "qlib_predictions_ready",
    "durable": True,
    "auto_delete": False,
    "arguments": {
        "x-message-ttl": 3600000,  # 1 hour TTL
        "x-max-length": 500,
        "x-overflow": "drop-head",
        "x-dead-letter-exchange": "dlx_reports",
        "x-dead-letter-routing-key": "report.predictions.failed"
    }
}
```

**Routing Key**: `qlib.predictions.ready`
**Exchange**: `khengleong.direct`
**Consumer Prefetch**: 2

**Publisher (Qlib Service)**:

```python
async def publish_predictions(request_id, report_id, predictions):
    connection = await connect_robust(rabbitmq_url)
    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        "khengleong.direct",
        type="direct",
        durable=True
    )

    message_body = {
        "request_id": request_id,
        "report_id": report_id,
        "timestamp": datetime.now().isoformat(),
        "prediction_status": "success",
        "predictions": predictions,
        "model_metadata": {...}
    }

    message = Message(
        body=json.dumps(message_body).encode(),
        delivery_mode=DeliveryMode.PERSISTENT,
        content_type="application/json",
        headers={
            "x-request-id": request_id,
            "x-source": "qlib_service"
        }
    )

    await exchange.publish(
        message,
        routing_key="qlib.predictions.ready"
    )

    logger.info(f"Published predictions for {request_id}")
    await connection.close()
```

**Consumer (Report Module in API.FastPy)**:

```python
# New consumer in API.FastPy/module/report/
async def start_predictions_consumer():
    connection = await connect_robust(rabbitmq_url)
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=2)

    queue = await channel.declare_queue(
        "qlib_predictions_ready",
        durable=True
    )

    async def process_predictions(message):
        async with message.process():
            try:
                data = json.loads(message.body.decode())
                request_id = data["request_id"]

                # Retrieve original extracted data
                extraction_data = await get_extraction_data(request_id)

                # Merge predictions with extracted data
                enriched_data = {**extraction_data, **data["predictions"]}

                # Generate Excel report
                report_path = await generate_report(request_id, enriched_data)

                # Publish to report_responses
                await publish_report_response(request_id, report_path)

            except Exception as e:
                logger.error(f"Failed to generate report: {e}")

    await queue.consume(process_predictions)
    logger.info("Started consuming qlib_predictions_ready queue")
```

---

### 4. Dead Letter Queues (DLQ)

```python
# DLQ for Qlib service failures
dlq_qlib_config = {
    "name": "qlib_predictions_dlq",
    "durable": True,
    "auto_delete": False,
    "arguments": {
        "x-message-ttl": 604800000,  # 7 days
    }
}

# DLX Exchange
dlx_config = {
    "name": "dlx_qlib",
    "type": "direct",
    "durable": True,
    "bindings": [
        {
            "queue": "qlib_predictions_dlq",
            "routing_key": "qlib.extraction.failed"
        }
    ]
}
```

---

## Exchange Configuration

### 1. khengleong.direct Exchange (NEW)

```python
exchange_config = {
    "name": "khengleong.direct",
    "type": "direct",
    "durable": True,
    "auto_delete": False,
    "bindings": [
        {
            "queue": "ai_extraction_complete",
            "routing_key": "ai.extraction.complete"
        },
        {
            "queue": "qlib_predictions_ready",
            "routing_key": "qlib.predictions.ready"
        }
    ]
}
```

---

## Message Acknowledgment Strategy

### AI Service → Qlib Service

- **Acknowledgment Mode**: Manual (explicit ack)
- **Requeue on Failure**: Yes (up to 3 retries)
- **Retry Delay**: Exponential backoff (5s, 10s, 20s)
- **DLQ Threshold**: After 3 failed retries

### Qlib Service → Report Module

- **Acknowledgment Mode**: Manual
- **Requeue on Failure**: No (prediction data stored in DB)
- **Retry Logic**: Handled at application level
- **Fallback**: Generate report without predictions

---

## Error Handling & Retry Logic

### Scenario 1: Qlib Service Down

```
AI Service publishes → ai_extraction_complete → (no consumer)
→ Message waits in queue (TTL: 1 hour)
→ If not consumed within 1 hour → Move to DLQ
→ Alert admin via monitoring
```

### Scenario 2: Qlib Prediction Fails

```
Qlib Service consumes → Processing fails → Requeue (retry count < 3)
→ Retry with exponential backoff
→ After 3 retries → Publish failure message to qlib_predictions_ready
→ Report Module generates report without predictions
```

### Scenario 3: Report Generation Fails

```
Report Module consumes predictions → Excel generation fails
→ Log error → Retry (3 times)
→ If still fails → Return error to user via report_responses
```

---

## Monitoring & Observability

### Metrics to Track

1. **Queue Depth**: Number of messages in each queue
2. **Message Age**: Time since message was published
3. **Processing Time**: Time to process each message
4. **Error Rate**: Failed messages per hour
5. **DLQ Size**: Number of messages in dead letter queues

### Alerts

- **Critical**: Queue depth > 100 for > 5 minutes
- **Warning**: Message age > 10 minutes
- **Info**: DLQ receives message

### RabbitMQ Management Commands

```bash
# Check queue status
rabbitmqadmin list queues name messages consumers

# Check queue depth
rabbitmqadmin get queue=ai_extraction_complete count=10

# Purge DLQ (admin only)
rabbitmqadmin purge queue name=qlib_predictions_dlq

# Check message rate
rabbitmqadmin list queues name messages_ready message_stats.publish_details.rate
```

---

## Security Configuration

### Authentication

```python
RABBITMQ_USERNAME = "khengleong_service"
RABBITMQ_PASSWORD = "<strong-password>"  # Stored in secrets
```

### Virtual Host

```python
RABBITMQ_VHOST = "/khengleong"  # Isolated virtual host
```

### Permissions

```bash
# Qlib Service user
rabbitmqctl set_permissions -p /khengleong qlib_service \
  "^(ai_extraction_complete|qlib_predictions_ready)$" \
  "^qlib_predictions_ready$" \
  "^ai_extraction_complete$"

# Read from ai_extraction_complete
# Write to qlib_predictions_ready
# No admin permissions
```

---

## Environment-Specific Configuration

### Development

```bash
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
QUEUE_PREFETCH=1
MESSAGE_TTL=600000  # 10 minutes
```

### Production

```bash
RABBITMQ_HOST=rabbitmq.khengleong.sg
RABBITMQ_PORT=5672
QUEUE_PREFETCH=2
MESSAGE_TTL=3600000  # 1 hour
RABBITMQ_USE_SSL=true
RABBITMQ_HEARTBEAT=60
```

---

## Connection Management

### Connection Pooling

```python
from aio_pika import connect_robust
from aio_pika.pool import Pool

connection_pool = Pool(
    lambda: connect_robust(rabbitmq_url),
    max_size=10,
    max_inactive_time=300  # 5 minutes
)

channel_pool = Pool(
    lambda: connection_pool.acquire().channel(),
    max_size=20
)
```

### Graceful Shutdown

```python
async def shutdown():
    logger.info("Shutting down RabbitMQ connection...")

    # Stop consuming
    await queue.cancel()

    # Close channel
    await channel.close()

    # Close connection
    await connection.close()

    logger.info("RabbitMQ connection closed")
```

---

## Testing

### Unit Tests

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_publish_extraction_complete():
    publisher = RabbitMQPublisher(mock_config)
    await publisher.publish_extraction_complete(
        request_id="test_123",
        data={"stocks": [...]}
    )

    assert publisher.channel.publish.called
    assert message.routing_key == "ai.extraction.complete"
```

### Integration Tests

```bash
# Start RabbitMQ in Docker
docker run -d --name rabbitmq-test \
  -p 5672:5672 -p 15672:15672 \
  rabbitmq:4.1-management

# Run integration test
pytest tests/integration/test_rabbitmq_flow.py
```

---

## Migration Strategy

### Phase 1: Deploy Qlib Service

1. Deploy Qlib service container
2. Create new queues and exchanges
3. **Do not** modify AI service yet

### Phase 2: Update AI Service

1. Update AI service to publish to both queues (old + new)
2. Monitor for errors
3. Validate messages in `ai_extraction_complete` queue

### Phase 3: Update Report Module

1. Add new consumer for `qlib_predictions_ready`
2. Keep existing report generation as fallback
3. Test end-to-end flow

### Phase 4: Cutover

1. Verify all components working
2. Remove old publish logic from AI service
3. Monitor for 48 hours

---

## Rollback Plan

If issues occur:

1. Stop Qlib service container
2. Revert AI service to publish only to old queues
3. Drain new queues: `rabbitmqadmin purge queue name=ai_extraction_complete`
4. Investigate and fix issues
5. Retry deployment

---

## Documentation Links

- [RabbitMQ Official Documentation](https://www.rabbitmq.com/documentation.html)
- [aio-pika Documentation](https://aio-pika.readthedocs.io/)
- [Dead Letter Exchanges](https://www.rabbitmq.com/dlx.html)
