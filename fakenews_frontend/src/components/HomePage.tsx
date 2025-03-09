import { Container, Box, Card, CardContent, CardMedia, Typography, CircularProgress, Alert } from '@mui/material';
import { getAllNews } from '../services/news';
import { useEffect, useState } from 'react';

// Define the type for the news article
interface NewsArticle {
    id: string; // Assuming each article has a unique ID, you can replace this with the appropriate type
    title: string;
    description: string;
    urlToImage?: string; // Optional property
}

function HomePage() {
    const [news, setNews] = useState<NewsArticle[]>([]); // Specify the type of the state
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchNews = async () => {
            try {
                const response = await getAllNews(); // Fetch the news
                const articles = response.articles; // Access articles array from the response
                if (Array.isArray(articles)) {
                    setNews(articles); // Set the state with the fetched news
                } else {
                    throw new Error('Fetched data is not an array');
                }
            } catch (error) {
                setError('Error fetching news. Please try again later.');
            } finally {
                setLoading(false);
            }
        };
        fetchNews(); // Run the fetch function
    }, []);

    if (loading) {
        return (
            <Container maxWidth="xl" sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
                <CircularProgress />
            </Container>
        );
    }

    if (error) {
        return (
            <Container maxWidth="xl" sx={{ textAlign: 'center', padding: '50px' }}>
                <Alert severity="error">{error}</Alert>
            </Container>
        );
    }

    return (
        <Container maxWidth="xl" sx={{ textAlign: 'center', padding: '50px', marginTop: '50px',marginLeft:'200px'  }}>
            <Box display="flex" flexWrap="wrap" justifyContent="center" mt={4} mb={4}>
                {news.length === 0 ? (
                    <Typography variant="h6" color="text.secondary">No news available.</Typography>
                ) : (
                    news.map((article, index) => (
                        <Card key={index} sx={{ maxWidth: 345, margin: 1.5 }}>
                            <CardMedia
                                component="img"
                                height="140"
                                image={article.urlToImage || '/default-image.jpg'} // Fallback image
                                alt={article.title || 'News Article'}
                            />
                            <CardContent>
                                <Typography gutterBottom variant="h5" component="div">
                                    {article.title}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    {article.description}
                                </Typography>
                            </CardContent>
                        </Card>
                    ))
                )}
            </Box>
        </Container>
    );
};

export default HomePage;
