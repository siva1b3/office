import pika
import time
import json

# Use RabbitMQ service name or container IP in Docker Compose
RABBITMQ_HOST = 'rabbitmq_app'   # Docker service name
RABBITMQ_PORT = 5672
RABBITMQ_USER = 'rabbitmq_user'
RABBITMQ_PASS = 'rabbitmq_password'
QUEUE_ADD = 'add_operations'
QUEUE_ADD_RESULT = 'add_result_queue'

def connect_to_rabbitmq():
    """Connects to RabbitMQ with retries."""
    retry_attempts = 10
    for i in range(retry_attempts):
        try:
            print(f"🔄 Attempting to connect to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT} (Attempt {i+1}/{retry_attempts})...")
            
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)
            )
            channel = connection.channel()
            
            # Declare queues (if they don't exist, create them)
            channel.queue_declare(queue=QUEUE_ADD, durable=True)
            channel.queue_declare(queue=QUEUE_ADD_RESULT, durable=True)
            
            print("✅ Connected to RabbitMQ and queues declared!")
            return connection, channel
        
        except Exception as e:
            print(f"❌ RabbitMQ connection failed: {e}")
            print("⏳ Retrying in 10 seconds...")
            time.sleep(10)
    
    print("❌ Failed to connect after multiple attempts. Exiting.")
    exit(1)

# Initialize connection and channel
connection, channel = connect_to_rabbitmq()


def callback(ch, method, properties, body):
    """Processes messages and publishes results."""
    try:
        data = json.loads(body)
        num1 = data.get("num1")
        num2 = data.get("num2")

        if num1 is not None and num2 is not None:
            result = num1 + num2
            print(f"✅ Addition result: {num1} + {num2} = {result}")

            # Publish result to result queue
            result_data = json.dumps({"num1": num1, "num2": num2, "result": result, "operation": "add"})
            ch.basic_publish(exchange='', routing_key=QUEUE_ADD_RESULT, body=result_data)

        else:
            print("⚠️ Invalid data received.")

        # Only acknowledge the message if the channel is open
        if ch.is_open:
            try:
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except pika.exceptions.ChannelClosedByBroker as e:
                print(f"⚠️ Channel closed before ack: {e}")
            except pika.exceptions.AMQPError as e:
                print(f"⚠️ AMQP error during ack: {e}")
            except Exception as e:
                print(f"❌ Unexpected error during ack: {e}")
        else:
            print("⚠️ Channel closed, skipping ack.")
    
    except json.JSONDecodeError:
        print("⚠️ Invalid JSON format received. Skipping...")
    except Exception as e:
        print(f"❌ Error processing message: {e}")

def start_consumer():
    """Starts consuming messages with channel recovery logic."""
    global connection, channel

    while True:
        try:
            print("🚀 Waiting for addition tasks. To exit, press CTRL+C")
            
            # Set auto_ack=False for manual acknowledgment
            channel.basic_consume(queue=QUEUE_ADD, on_message_callback=callback, auto_ack=False)
            
            channel.start_consuming()

        except pika.exceptions.ChannelClosedByBroker as e:
            print(f"⚠️ Channel closed by broker: {e}. Reconnecting...")
            time.sleep(5)
            connection, channel = connect_to_rabbitmq()

        except pika.exceptions.AMQPConnectionError as e:
            print(f"❌ Connection error: {e}. Reconnecting...")
            time.sleep(5)
            connection, channel = connect_to_rabbitmq()

        except KeyboardInterrupt:
            print("🛑 Exiting...")
            connection.close()
            break

# Start the consumer
start_consumer()

