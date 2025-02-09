import express from "express";
import cors from "cors";
import multer from "multer";
import pkg from "pg";
import axios from "axios";
import FormData from "form-data";

const { Pool } = pkg;
const app = express();
app.use(cors());
app.use(express.json());

const port = 3001;
const flaskUrl = "http://python_app:5000/upload"; // Correct Flask container name

const pool = new Pool({
  user: "admin",
  host: "postgres_db",
  database: "my_database",
  password: "admin123",
  port: 5432,
});

// Use memory storage for multer to send buffer data
const storage = multer.memoryStorage();
const upload = multer({ storage });

app.post("/upload_image", upload.single("image"), async (req, res) => {
  if (!req.file)
    return res.status(400).json({ success: false, message: "No file" });
  const algorithm = req.body.selectedOption; // dropdown value
  const threshold = req.body.threshold; // threshold value

  try {
    const formData = new FormData();
    formData.append("image", req.file.buffer, {
      filename: req.file.originalname,
      contentType: req.file.mimetype,
    });

    const { data } = await axios.post(flaskUrl, formData, {
      headers: formData.getHeaders(),
    });

    if (data.status_image !== 1)
      return res
        .status(400)
        .json({ success: false, message: "Flask rejected image" });

    const query = `INSERT INTO image_data (image_name, image_url,algorithm,threshold) VALUES ($1, $2, $3, $4) RETURNING *`;
    const result = await pool.query(query, [
      req.file.originalname,
      `/uploads/${req.file.originalname}`,
      algorithm,
      threshold,
    ]);

    res.status(201).json({
      success: true,
      status_image: data.status_image,
      data: result.rows[0],
    });
  } catch (error) {
    console.error("Error processing image:", error.message);
    res.status(500).json({ success: false, message: "Error processing image" });
  }
});

pool.connect().then(() => {
  console.log("Database connected");
  app.listen(port, () =>
    console.log(`Server running on http://localhost:${port}`)
  );
});
