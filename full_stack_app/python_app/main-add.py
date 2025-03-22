import pika
import json
import os
import time

RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "admin")
# RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq-service")  # Update with your service name
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")  # Update with your service name
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
connection_params = pika.ConnectionParameters(
    host=RABBITMQ_HOST,
    port=int(RABBITMQ_PORT),
    credentials=credentials,
    heartbeat=600,  # Prevents timeout issues
    blocked_connection_timeout=300,  # Avoids blocking indefinitely
)


def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        num1 = data.get("num1")
        num2 = data.get("num2")
        if num1 is not None and num2 is not None:
            result = num1 + num2
            print(f"Addition result: {num1} + {num2} = {result}")
            
            # Publish result to result_queue
            result_data = json.dumps({"num1": num1, "num2": num2, "result": result})
            ch.basic_publish(exchange='', routing_key='add_result_queue', body=result_data)
        else:
            print("Invalid data received.")
    except Exception as e:
        print(f"Error processing message: {e}")
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Set up connection to RabbitMQ
# Retry connecting to RabbitMQ if it is not ready
while True:
    try:
        print(f"🔄 Attempting to connect to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}...")
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        print("✅ Connected to RabbitMQ!")
        break
    except Exception as e:
        print(f"❌ RabbitMQ connection failed: {e}")
        print("⏳ Retrying in 5 seconds...")
        time.sleep(5)

# Declare queues
channel.queue_declare(queue='add_operations', durable=True)
channel.queue_declare(queue='add_result_queue', durable=True)

# Start consuming messages
channel.basic_consume(queue='add_operations', on_message_callback=callback)

print("Waiting for addition tasks. To exit, press CTRL+C")
channel.start_consuming()
