import express, { Request, Response } from "express";
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();

const PORT = process.env.PORT || 3000;
const FLASK_URL = process.env.FLASK_URL || 'http://127.0.0.1:5000';

app.use(cors());

// Generic JSON proxy helper
async function proxyJson(flaskPath: string, res: Response): Promise<void> {
    try {
        const response = await fetch(`${FLASK_URL}${flaskPath}`);
        const data = await response.json();
        res.status(response.status).json(data);
    } catch (error) {
        res.status(500).json({ error: 'Flask server error' });
    }
}

// Generic binary (image) proxy helper
async function proxyBinary(flaskPath: string, res: Response): Promise<void> {
    try {
        const response = await fetch(`${FLASK_URL}${flaskPath}`);
        if (!response.ok) {
            res.status(response.status).json({ error: 'Flask server error' });
            return;
        }
        const contentType = response.headers.get('Content-Type') || 'image/png';
        const buffer = await response.arrayBuffer();
        res.set('Content-Type', contentType);
        res.send(Buffer.from(buffer));
    } catch (error) {
        res.status(500).json({ error: 'Flask server error' });
    }
}

app.get('/analyze', async (req: Request, res: Response): Promise<void> => {
    await proxyJson('/analyze', res);
});

app.get('/stocks/apple', async (req: Request, res: Response): Promise<void> => {
    await proxyJson('/stocks/apple', res);
});

app.get('/stocks/amazon', async (req: Request, res: Response): Promise<void> => {
    await proxyJson('/stocks/amazon', res);
});

app.get('/stocks/microsoft', async (req: Request, res: Response): Promise<void> => {
    await proxyJson('/stocks/microsoft', res);
});

app.get('/stocks/nvidia', async (req: Request, res: Response): Promise<void> => {
    await proxyJson('/stocks/nvidia', res);
});

// Plot image proxy — returns PNG chart from Flask
app.get('/plot/window/:stock/:time', async (req: Request, res: Response): Promise<void> => {
    const { stock, time } = req.params;
    await proxyBinary(`/plot/window/${stock}/${time}`, res);
});

// Plotly interactive HTML chart proxy — returned into an <iframe>
app.get('/chart/plotly/:stock/:time', async (req: Request, res: Response): Promise<void> => {
    const { stock, time } = req.params;
    try {
        const response = await fetch(`${FLASK_URL}/chart/plotly/${stock}/${time}`);
        if (!response.ok) {
            res.status(response.status).json({ error: 'Flask server error' });
            return;
        }
        const html = await response.text();
        res.set('Content-Type', 'text/html');
        res.send(html);
    } catch (error) {
        res.status(500).json({ error: 'Flask server error' });
    }
});

app.listen(PORT, (): void => {
    console.log(`Listening on PORT ${PORT}`);
});