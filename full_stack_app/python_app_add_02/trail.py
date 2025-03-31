import pika
import time
import json

# Use RabbitMQ service name or container IP in Docker Compose
RABBITMQ_HOST = 'rabbitmq-service'   # Docker service name
RABBITMQ_PORT = 5672
RABBITMQ_USER = 'rabbitmq_user'
RABBITMQ_PASS = 'rabbitmq_password'

# Establish connection with retry logic
MAX_RETRIES = 15
RETRY_DELAY = 10  # seconds

credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
parameters = pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials)

connection = None
for attempt in range(1, MAX_RETRIES + 1):
    try:
        connection = pika.BlockingConnection(parameters)
        print("Connected to RabbitMQ")
        break
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Connection attempt {attempt} failed: {e}")
        if attempt < MAX_RETRIES:
            print(f"Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
        else:
            print("Max retries reached. Exiting...")
            exit(1)

channel = connection.channel()
# Set prefetch count to 1 for fair dispatch
channel.basic_qos(prefetch_count=1)

# Define queues
CONSUME_QUEUES = ["add_operations"]
PRODUCE_QUEUES = ["add_result_queue"]

ALL_QUEUES = CONSUME_QUEUES + PRODUCE_QUEUES

# Ensure queues exist
for queue in ALL_QUEUES:
    try:
        channel.queue_declare(queue=queue, durable=True, passive=True)
    except pika.exceptions.ChannelClosedByBroker:
        print(f"Queue {queue} does not exist. Creating it...")
        channel = connection.channel()
        channel.queue_declare(queue=queue, durable=True)

def process_message(queue_name, data):
    time.sleep(10)
    if isinstance(data, dict) and "num1" in data and "num2" in data:
        operation_map = {
            "add_operations": (lambda x, y: x + y, "add_result_queue", "add"),
            "sub_operations": (lambda x, y: x - y, "sub_result_queue", "sub"),
            "mul_operations": (lambda x, y: x * y, "mul_result_queue", "mul"),
            "div_operations": (lambda x, y: x / y if y != 0 else None, "div_result_queue", "div"),
        }
        
        if queue_name in operation_map:
            operation, result_queue, operation_name = operation_map[queue_name]
            num1, num2 = data["num1"], data["num2"]
            result = operation(num1, num2)
            if result is not None:
                result_data = {"num1": num1, "num2": num2, "result": result, "operation": operation_name}
                send_to_queue(result_queue, result_data)
                print(f"Processed {queue_name} and sent result to {result_queue}: {result}")
            else:
                print("Invalid operation (e.g., division by zero)")
    else:
        print("Invalid data format")

def send_to_queue(queue_name, data):
    channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(data), properties=pika.BasicProperties(delivery_mode=2))
    print(f"Sent to {queue_name}: {data}")

def callback(ch, method, properties, body):
    try:
        message_str = body.decode("utf-8")  # Decode byte string
        message_dict = json.loads(message_str)  # Convert JSON string to dict
        print(f"Received from {method.routing_key}: {message_dict}, Type: {type(message_dict)}")
        process_message(method.routing_key, message_dict)  # Pass dict to function
    except json.JSONDecodeError:
        print("Error decoding JSON message")
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Start consuming from operation queues
for queue_name in CONSUME_QUEUES:
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)
    print(f"Consuming messages from queue: {queue_name}")

print("Waiting for messages. To exit, press CTRL+C")
channel.start_consuming()
