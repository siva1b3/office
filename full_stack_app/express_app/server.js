import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import amqp from "amqplib";
import pkg from "pg";
import cors from "cors";
import { v4 as uuidv4 } from "uuid"; // ✅ Import UUID for unique client ID

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(cors());
app.use(express.json());
const PORT = process.env.PORT || 3001;

const { Pool } = pkg;

// PostgreSQL Connection Pool
const pool = new Pool({
  user: "admin_user",
  host: "postgres-service",
  database: "mydatabase",
  password: "admin_password",
  port: 5432,
});

// RabbitMQ Credentials
const RABBITMQ_USER = "rabbitmq_user";
const RABBITMQ_PASS = "rabbitmq_password";
const RABBITMQ_HOST = "rabbitmq-service";
const RABBITMQ_URL = `amqp://${RABBITMQ_USER}:${RABBITMQ_PASS}@${RABBITMQ_HOST}:5672`;

// Request Queue
const QUEUE_ADD = "add_operations";
const QUEUE_SUB = "sub_operations";
const QUEUE_MUL = "mul_operations";
const QUEUE_DIV = "div_operations";

// Response Queue
const QUEUE_ADD_RESULT = "add_result_queue";
const QUEUE_SUB_RESULT = "sub_result_queue";
const QUEUE_MUL_RESULT = "mul_result_queue";
const QUEUE_DIV_RESULT = "div_result_queue";

const queues_list = [
  QUEUE_ADD,
  QUEUE_SUB,
  QUEUE_MUL,
  QUEUE_DIV,
  QUEUE_ADD_RESULT,
  QUEUE_SUB_RESULT,
  QUEUE_MUL_RESULT,
  QUEUE_DIV_RESULT,
];

const request_queue_list = {
  add: QUEUE_ADD,
  subtract: QUEUE_SUB,
  multiply: QUEUE_MUL,
  divide: QUEUE_DIV,
};

const response_queue_list = [
  QUEUE_ADD_RESULT,
  QUEUE_SUB_RESULT,
  QUEUE_MUL_RESULT,
  QUEUE_DIV_RESULT,
];

const RETRIES = 10;
const DELAY = 10000;

let rabbitConnection;
let rabbitChannel;

// Start Express Server
app.use(express.static(path.join(__dirname, "public")));

app.post("/calculate", async (req, res) => {
  const { num1, num2, operation } = req.body;

  if (num1 === undefined || num2 === undefined || !operation) {
    return res.status(400).json({ error: "Missing parameters" });
  }

  if (!request_queue_list[operation])
    return res.status(400).json({ error: "Invalid operation" });

  const request_status = await sendMessage(
    { num1, num2, operation },
    request_queue_list[operation]
  );

  if (!request_status) {
    return res.status(500).json({ error: "Failed to send message to queue" });
  }

  return res.json({
    success: true,
    message: `Processing request: ${operation}`,
  });
});

const clients = {}; // Store client connections by clientId
const taskResults = {}; // Store pending results

// SSE Endpoint for Real-time Updates
app.get("/events", (req, res) => {
  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");

  const clientId = uuidv4(); // Unique ID for each client
  clients[clientId] = res; // Store the connection
  console.log(`Client connected: ${clientId}`);

  // Send client ID to the client
  res.write(`event: clientId\ndata: ${clientId}\n\n`);

  // Check for pending results and send them if they exist
  if (taskResults[clientId]) {
    res.write(`data: ${taskResults[clientId]}\n\n`);
    delete taskResults[clientId]; // Clean up after sending
  }

  // Remove client on disconnect
  req.on("close", () => {
    console.log(`Client disconnected: ${clientId}`);
    delete clients[clientId];
  });
});

// ✅ Send updates to a specific client by clientId
const sendUpdate = (clientId, data) => {
  if (clients[clientId]) {
    clients[clientId].write(`data: ${JSON.stringify(data)}\n\n`);
    console.log(`Sent update to client ${clientId}`);
  } else {
    console.log(`Client ${clientId} not connected. Storing result.`);
    taskResults[clientId] = JSON.stringify(data); // Store for later if disconnected
  }
};

app.get("/", (req, res) => {
  console.log("🔄 Serving index.html");
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.listen(PORT, "0.0.0.0", async () => {
  try {
    await connectRabbitMQ();
    consumeResults(response_queue_list);
  } catch (error) {
    console.error("❌ RabbitMQ connection failed:", error);
  }
  console.log(`✅ Server is running on http://localhost:${PORT}`);
});

async function connectRabbitMQ(retries = RETRIES, delay = DELAY) {
  for (let i = 0; i < retries; i++) {
    try {
      console.log(
        `⏳ Attempting to connect to RabbitMQ (${i + 1}/${retries})...`
      );
      rabbitConnection = await amqp.connect(RABBITMQ_URL);
      rabbitChannel = await rabbitConnection.createChannel();
      console.log("✅ Connected to RabbitMQ and channel is ready");

      // Create a persistent queue after connection is established
      await create_predined_queus(queues_list); // Replace "tasks" with your desired queue name
      return;
    } catch (error) {
      console.error(
        `❌ RabbitMQ connection attempt ${i + 1} failed:`,
        error.message
      );
      if (i < retries - 1) {
        console.log(`🔄 Retrying in ${delay / 1000} seconds...`);
        await new Promise((res) => setTimeout(res, delay));
      }
    }
  }
  throw new Error("❌ Failed to connect to RabbitMQ after multiple attempts");
}

async function create_predined_queus(queues_list) {
  // Null guard clause: Check if queues_list is valid and has at least one queue
  if (!Array.isArray(queues_list) || queues_list.length === 0) {
    console.warn(
      "❌ queues_list is empty or not an array. No queues were created."
    );
    return null; // Return early if the input is invalid
  }

  // Validate that all elements are strings and have length > 1
  for (const queue of queues_list) {
    if (typeof queue !== "string" || queue.length <= 0) {
      console.error(
        `❌ Invalid queue name: "${queue}". Queue names must be strings with length > 1.`
      );
      return null; // Stop execution if any queue name is invalid
    }
  }

  if (!rabbitChannel) {
    throw new Error("❌ RabbitMQ channel is not available");
  }

  for (const queue of queues_list) {
    try {
      // Assert the queue exists or create it if it doesn't
      await rabbitChannel.assertQueue(queue, { durable: true });
      // durable: true makes the queue persistent
      console.log(`✅ Queue "${queue}" is ready (durable)`);
    } catch (error) {
      console.error(`❌ Failed to create queue ${queue}:`, error.message);
      throw error;
    }
  }
}

async function sendMessage(message, queueName) {
  if (!rabbitChannel) {
    throw new Error("❌ RabbitMQ channel is not available");
  }

  try {
    // Convert the message object to a JSON string
    const messageString = JSON.stringify(message);

    // Send message to the queue with persistent flag
    rabbitChannel.sendToQueue(queueName, Buffer.from(messageString), {
      persistent: true,
    });
    console.log(`✅ Message sent to queue "${queueName}":`, message);
    return true;
  } catch (error) {
    console.error(
      `❌ Failed to send message to queue "${queueName}":`,
      error.message
    );
    return false;
  }
}

async function consumeResults(response_queue_list) {
  await Promise.all(
    response_queue_list.map(async (queue) => {
      rabbitChannel.consume(queue, async (msg) => {
        if (!msg) return;

        const result = JSON.parse(msg.content.toString());
        console.log(`📥 Received from ${queue}:`, result);

        if (typeof result?.result !== "number") {
          console.warn(`⚠️ Invalid result received from ${queue}:`, result);
        } else {
          // await new Promise((resolve) => setTimeout(resolve, 30000));
          await storeResult(result);
          sendUpdate(result);
        }

        rabbitChannel.ack(msg);
      });
    })
  );
}

async function storeResult(result) {
  const { operation, num1, num2, result: operation_result } = result;
  try {
    await pool.query(
      "INSERT INTO operations (operation_type,number_1, number_2, operation_result) VALUES ($1, $2, $3, $4)",
      [operation, num1, num2, operation_result]
    );
    console.log("✅ Result stored in database");
  } catch (error) {
    console.error("❌ Database insert failed", error);
  }
}
