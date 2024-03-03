const express = require('express');
const cors = require('cors');
const { ApifyClient } = require('apify-client');

const app = express();
const port = 3000;

const client = new ApifyClient({
    token: 'apify_api_SO4LvWFkmdsaSiI7io6hfEF6KDJHAN0gsfiv',
});

// Use CORS middleware
app.use(cors());

app.use(express.json());

app.post('/scrape', async (req, res) => {
    const input = req.body;
    try {
        const run = await client.actor("BG3WDrGdteHgZgbPK").call(input);
        const { items } = await client.dataset(run.defaultDatasetId).listItems();
        res.json(items);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(port, () => {
    console.log(`Server listening at http://localhost:${port}`);
});
