import express from "express";
import path from "path";
import cors from "cors";
import amqp from "amqplib";
import pkg from "pg";

const app = express();
const PORT = 3001;

// Serve static files from the "public" folder
const __dirname = path.resolve();
app.use(express.static(path.join(__dirname, "public")));

// RabbitMq Credentials
const RABBITMQ_USER = "rabbitmq_user";
const RABBITMQ_PASS = "rabbitmq_password";
const RABBITMQ_HOST = "rabbitmq_app";
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

const { Pool } = pkg;

// PostgreSQL Connection Pool
const pool = new Pool({
  user: "admin_user",
  host: "postgres_app",
  database: "mydatabase",
  password: "admin_password",
  port: 5432,
});

// Variables
let connection, channel;
// ✅ Local variable cache to store results temporarily
let resultCache;
const clients = new Set();

app.use(cors());
app.use(express.json()); // Middleware to parse JSON requests
app.use(express.static("public")); // Serve static files

async function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Create Channel and Queues
async function createChannel() {
  try {
    console.log("⏳ Waiting 2 seconds before connecting...");

    await delay(30000); // Wait for 2 seconds

    console.log("⏳ Connecting to RabbitMQ...");

    connection = await amqp.connect(RABBITMQ_URL);

    channel = await connection.createChannel();

    console.log("✅ Connected to RabbitMQ");

    const queues = [
      QUEUE_ADD,
      QUEUE_SUB,
      QUEUE_MUL,
      QUEUE_DIV,
      QUEUE_ADD_RESULT,
      QUEUE_SUB_RESULT,
      QUEUE_MUL_RESULT,
      QUEUE_DIV_RESULT,
    ];
    for (const queue of queues) {
      await channel.assertQueue(queue, { durable: true });
    }
    console.log("✅ Queues initialized");
  } catch (error) {
    console.error("❌ Failed to connect to RabbitMQ", error);
  }
}

// Send message to RabbitMQ queue
async function sendToQueue(message, queue) {
  if (!channel) return console.error("❌ RabbitMQ channel not initialized");
  try {
    channel.sendToQueue(queue, Buffer.from(JSON.stringify(message)), {
      persistent: true,
    });
    console.log(`✅ Sent to queue '${queue}':`, message);
  } catch (error) {
    console.error(`❌ Error sending message to queue '${queue}':`, error);
  }
}

// Route to serve the HTML file
app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

// Backend code for calculates
app.post("/calculate", async (req, res) => {
  const { num1, num2, operation } = req.body;

  if (num1 === undefined || num2 === undefined || !operation) {
    return res.status(400).json({ error: "Missing parameters" });
  }
  const queueMap = {
    add: QUEUE_ADD,
    subtract: QUEUE_SUB,
    multiply: QUEUE_MUL,
    divide: QUEUE_DIV,
  };
  if (!queueMap[operation])
    return res.status(400).json({ error: "Invalid operation" });

  await sendToQueue({ num1, num2, operation }, queueMap[operation]);
  res.json({ success: true, message: `Processing request: ${operation}` });
});

//Store the result into database
async function storeResult(num1, num2, operation, result) {
  try {
    await pool.query(
      "INSERT INTO results (num1, num2, operation, result) VALUES ($1, $2, $3, $4)",
      [num1, num2, operation, result]
    );
    console.log("✅ Result stored in database");
  } catch (error) {
    console.error("❌ Database insert failed", error);
  }
}

// fetch the result from database
/*app.get("/results", async (req, res) => {
  try {
    const { rows } = await pool.query(
      "SELECT * FROM results ORDER BY result_id DESC LIMIT 10"
    );
    res.json(rows);
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch results" });
  }
});*/

app.get("/results", async (req, res) => {
  try {
    res.json(resultCache[0]);
  } catch (error) {
    res.status(500).json({ error: "Failed to fetch results" });
  }
});
// ✅ Consume results from RabbitMQ and store in cache
async function consumeResults() {
  const resultQueues = [
    QUEUE_ADD_RESULT,
    QUEUE_SUB_RESULT,
    QUEUE_MUL_RESULT,
    QUEUE_DIV_RESULT,
  ];

  for (const queue of resultQueues) {
    channel.consume(queue, async (msg) => {
      if (msg !== null) {
        const result = JSON.parse(msg.content.toString());
        console.log(`📥 Received from ${queue}:`, result);
	console.log(`📥 Received from ${queue}:`, result["result"]);
        // // Store result in the local cache
        // resultCache.push({
        //   num1: result.num1,
        //   num2: result.num2,
        //   operation: queue.replace("_result_queue", ""),
        //   result: result.result,
        //   timestamp: new Date().toISOString(),
        // });

        // // Limit cache to the last 20 results
        // if (resultCache.length > 20) {
        //   resultCache.shift(); // Remove the oldest result
        // }

        // Store result in DB for persistence
        // await storeResult(
        //   result.num1,
        //   result.num2,
        //   queue.replace("_result_queue", ""),
        //   result.result
        // );

        // Acknowledge message
        channel.ack(msg);
      }
    });
  }
}

// ✅ Start the server only after RabbitMQ connection is established
createChannel()
  .then(() => {
    consumeResults();
    app.listen(PORT, "0.0.0.0", () => {
      console.log(`🚀 Server running on http://0.0.0.0:${PORT}`);
    });
  })
  .catch((err) => {
    console.error(
      "❌ Could not start the server because RabbitMQ connection failed:",
      err
    );
  });
